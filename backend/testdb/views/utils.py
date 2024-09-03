# Standard library imports
import os
import datetime
import numbers
import json
import ast

# Django imports
from django.apps import apps
from django.utils.timezone import make_aware

# Third-party imports
import pandas as pd
import duckdb

# Local imports
from ..models import Question, Answer, Datasheet, Conversation, Component

import numpy as np
from scipy import stats

from ollama import Client

# Constants
APP_CONFIG = apps.get_app_config('testdb')
MODEL = os.environ.get('OLLAMA_MODEL')
# LLM = ChatOllama(model=os.environ.get('OLLAMA_MODEL'), base_url=os.environ.get('OLLAMA_PATH'))
server_client = Client(host=os.environ.get('OLLAMA_PATH'))
local_client = Client(host=os.environ.get('LOCAL_OLLAMA_PATH'))
CON = duckdb.connect()

def add_datasheet_from_upload(request):
    """
    Add a new datasheet from an uploaded file.

    Args:
        request: The HTTP request object containing the uploaded file and metadata.

    Returns:
        str: The name of the created datasheet.
    """
    datasheet_name = request.POST.get('datasheet_name').replace(' ', '_')
    user = request.POST.get('user', '-')
    user_email = request.POST.get('user_email', '-')
    user_group = request.POST.get('user_group', '-')

    data_files = request.FILES.getlist('data_file')
    data_file = data_files[0] if data_files else None

    # Create or get existing datasheet
    datasheet, created = Datasheet.objects.get_or_create(
        datasheet_name=datasheet_name,
        defaults={
            'datasheet_size': 0,
            'user': user,
            'user_email': user_email,
            'user_group': user_group,
            'datasheet_date_time': make_aware(datetime.datetime.now())
        }
    )

    # Create directory for pdfs if it doesn't exist
    os.makedirs(f'data/{datasheet_name}', exist_ok=True)
    
    if data_file:
        datasheet.data_file.save(f'{datasheet_name}/attachment.csv', data_file, save=True)

    return datasheet_name

def recommend_plot(name: str) -> dict:
    """
    Recommend a plot type based on the data in the datasheet.

    Args:
        name (str): The name of the datasheet.

    Returns:
        dict: A dictionary containing the recommended plot type and data.
    """
    datasheet = Datasheet.objects.get(datasheet_name=name)
    data = pd.read_csv(datasheet.data_file.path)

    numerical_columns = data.select_dtypes(include=['number']).columns
    categorical_columns = data.select_dtypes(exclude=['number']).columns
    num_numeric = len(numerical_columns)
    num_categorical = len(categorical_columns)

    has_category_duplicates = False
    if categorical_columns.any():
        has_category_duplicates = len(data[categorical_columns[0]]) != len(set(data[categorical_columns[0]]))

    if num_categorical == 2 and num_numeric == 1:
        return {
            "type": "bar",
            "data": [{'name': name, 'value': value, 'category': category} 
                     for name, value, category in zip(data[categorical_columns[0]], 
                                                      data[numerical_columns[0]], 
                                                      data[categorical_columns[1]])]
        }
    elif num_categorical == 1 and num_numeric > 1 and has_category_duplicates:
        return {
            "type": "heatmap",
            "data": [{"row_name": row, "column_name": col, "count": value} 
                     for col in numerical_columns 
                     for row, value in zip(data[categorical_columns[0]], data[col])]
        }
    elif num_categorical == 1 and num_numeric == 1 and has_category_duplicates:
        return {
            "type": "density",
            "data": [{"value": value, "group": group} 
                     for group, value in zip(data[categorical_columns[0]], data[numerical_columns[0]])]
        }
    elif num_categorical == 1 and num_numeric == 1 and not has_category_duplicates:
        return {
            "type": "pie",
            "data": [{"category": category, "value": value} 
                     for category, value in zip(data[categorical_columns[0]], data[numerical_columns[0]])]
        }
    elif num_numeric >= 1:
        box_data = []
        for col in numerical_columns:
            if categorical_columns.any():
                box_data.append({"name": col, "values": data[col].tolist(), "group": data[categorical_columns[0]].tolist()})
            else:
                box_data.append({"name": col, "values": data[col].tolist()})
        return {
            "type": "box",
            "data": box_data
        }
    return 'none'

def format_data(json_obj: dict) -> dict:
    """
    Format data based on the plot type and library name.

    Args:
        json_obj (dict): A dictionary containing plot information.

    Returns:
        dict: Formatted data for the specified plot type.
    """
    plot_type = json_obj['plot_type']
    library_name = json_obj['library_name']
    datasheet = Datasheet.objects.get(datasheet_name=library_name)
    data = pd.read_csv(datasheet.data_file.path)
    data.fillna(0, inplace=True)

    if plot_type == "bar":
        return {
            "data": [{'name': name, 'value': value, 'category': category} 
                     for name, value, category in zip(data[json_obj['category_column']], 
                                                      data[json_obj['value_column']], 
                                                      data[json_obj['group_column']]) 
                     if isinstance(value, numbers.Number)]
        }
    elif plot_type == "heatmap":
        all_rows = data[json_obj['row_names_from']].tolist()
        picked_rows = json_obj['rows']
        row_indices = [i for i, row in enumerate(all_rows) if row in picked_rows]
        rows = [row for row in all_rows if row in picked_rows]

        return {
            "data": [{"row_name": row, "column_name": col, "count": value} 
                     for col in json_obj['columns'] 
                     for row, value in zip(rows, [data[col][i] for i in row_indices]) 
                     if isinstance(value, numbers.Number)]
        }
    elif plot_type == "density":
        return {
            "data": [{"value": value, "group": group} 
                     for group, value in zip(data[json_obj['group_column']], data[json_obj['value_column']]) 
                     if isinstance(value, numbers.Number)]
        }
    elif plot_type == "pie":
        return {
            "data": [{"category": category, "value": value} 
                     for category, value in zip(data[json_obj['group_column']], data[json_obj['value_column']]) 
                     if isinstance(value, numbers.Number)]
        }
    elif plot_type == "box":
        return {
            "data": [{"name": col, "values": data[col].tolist()} for col in json_obj['categories']]
        }
    return 'none'

def style_component(prompt: str, conversation_id: str) -> str:
    """
    Create a conversation chain for style-related questions.

    Args:
        conversation_id (str): The ID of the conversation.

    Returns:
        str: The response from the language model.
    """
    conversation = Conversation.objects.get(id=int(conversation_id))
    component_info = Component.objects.latest("id").component_info
    questions = [obj.question_text for obj in Question.objects.filter(conversation=conversation, question_type="STYLE").order_by('id')]
    answers = [obj.answer_text for obj in Answer.objects.filter(conversation=conversation, answer_type="STYLE").order_by('id')]

    history = ""

    for q, a in zip(questions, answers):
        history += f"User: {q}\n"
        history += f"AI Assistant: {a}\n"
    print(history)

    llm_prompt = f"""
    The following is a friendly conversation between a human and an AI. If the AI does not know the answer to a question, it truthfully says it does not know.
    During the conversation, an interface for a react component will be provided. The AI is tasked with iterating on the JSON interface in accordance with user requests.
    If the AI thinks it should change something in the interface, it should detail exactly what must be changed to meet a user request.
    Always include the entire interface with any changes at the very end of the message. Never abbreviate anything.
    The AI Assistant message must be able to be parsed such that correctly formatted JSON interface can be extracted from the message with python.
    Only include the JSON interface at the end of the message. The beginning of the message should consist of conversation and answers.
    The interface json should be enclosed in <JSON> and </JSON> tags as defined by FORMAT.
    FORMAT:  <JSON>*full, unabbreviated json goes here*</JSON>

    Component Interface and Instructions:
    {component_info}

    Conversation:
    {history}
    User: {prompt}
    """

    print("Styling Prompt: ", llm_prompt)
    response = server_client.generate(os.environ.get('OLLAMA_MODEL'), llm_prompt)
    answer = response['response']
    print(answer)
    return answer.replace('\n', '')

def get_sql_code(prompt: str, num_cols: str, cat_cols: str, error: str = '') -> str:
    """
    Generate SQL code based on the given prompt and column information.

    Args:
        prompt (str): The question or prompt for generating SQL.
        num_cols (str): Formatted string of numerical column names.
        cat_cols (str): Formatted string of categorical column names.
        error (str, optional): Error message from previous attempt, if any.

    Returns:
        str: Generated SQL code.
    """
    example = """
Example Question:
What cancer is least dependent on OR4?

Example Table name: input_table

Example Numerical column names:
1. "Bile Duct Cancer"
2. "Bladder Cancer"
3. "Bone Cancer"
4. "Brain Cancer"
5. "Breast Cancer"
6. "Cervical Cancer"
7. "Colon/Colorectal Cancer"

Example Categorical columns:
1. Family_name

Example Output:
```sql
-- Select the cancer type with the lowest value for OR4
WITH cancer_values AS (
  SELECT 
    'Bile Duct Cancer' AS cancer_type, "Bile Duct Cancer" AS value
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Bladder Cancer', "Bladder Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Bone Cancer', "Bone Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Brain Cancer', "Brain Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Breast Cancer', "Breast Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Cervical Cancer', "Cervical Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
  UNION ALL
  SELECT 'Colon/Colorectal Cancer', "Colon/Colorectal Cancer"
  FROM input_table
  WHERE Family_name = 'OR4'
)
SELECT 
  cancer_type AS least_dependent_cancer,
  value AS min_value
FROM cancer_values
ORDER BY value ASC
LIMIT 1;
```
"""
    sql_prompt = f"""
You are an AI assistant specialized in generating SQL queries for DuckDB. Given a question and the names of numerical and categorical columns in a data table, your task is to generate SQL code that can be run in DuckDB to retrieve the information necessary to answer the question. All column names will be provided as either categorical or numerical, do not assume there are any more columns.

Please generate a SQL query that will retrieve the relevant data to answer the question. Follow these guidelines:

1. Use appropriate SQL clauses (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY) as needed.
2. Include any necessary aggregations (COUNT, SUM, AVG, MAX, MIN, STDDEV) if required by the question, remembering that aggregate functions can not be nested.
3. Use appropriate joins if the question implies the need for data from multiple tables.
4. Include comments to explain the purpose of each part of the query.
5. If any assumptions are made about the data or the question, state them clearly.
6. If additional information is needed to generate a more accurate query, mention it.
7. Write the entire SQL query in a block that can be easily parsed out and ran programatically.
8. Ensure all column names with spaces are enclosed in double quotes.
9. Use DuckDB-specific syntax where necessary (e.g., for pivot operations or complex type handling).
10. Sometimes you will be provided with a error reflecting a failed previous attempt. Use the error as guidance in writing the code.
11. Use STDDEV instead of STDEV.
12. Assume every column name is in snake_case. For example, if the prompt references Black Cats, the SQL query should instead use black_cats.

Example:
{example}

Your Turn:

Question: {prompt}

Table name: input_table

Numerical column names:
{num_cols}

Categorical column names:
{cat_cols}

{error}

Generate the SQL query below:
"""
    output = server_client.generate(MODEL, sql_prompt)
    response = output['response']
    code = response[response.find("```sql")+6:response.rfind("```")]

    try:
        sql_result = CON.sql(code).df()
        print('CODE: ', code)
        print('RESULT: ', sql_result)
        return sql_result
    except Exception as e:
        error_message = f"""
Previous Code:
{code}
Code Error:
{str(e)}
"""
        print(error_message)
        new_code = get_sql_code(prompt, num_cols, cat_cols, error_message)
        return 'Failed.'
    
def ttest(col_1: str, col_2: str, conversation_id: str) -> str:
    conversation = Conversation.objects.get(id=int(conversation_id))
    datasheet = conversation.conversation_datasheet
    df = pd.read_csv(datasheet.data_file)
    cols = list(df.columns)
    new_cols = [x.replace(' ', '_').lower() for x in cols]
    df = df.rename(columns=dict(zip(cols, new_cols)))
    col_name_1 = col_1.replace(' ', '_').lower()
    col_name_2 = col_2.replace(' ', '_').lower()
    if col_name_1 not in new_cols or col_name_2 not in new_cols:
        return "At least one of the provided columns cannot be found in this datasheet."
    x = df[col_name_1].to_list()
    y = df[col_name_2].to_list()
    t_stat, p_val = stats.ttest_ind(x, y)
    return f"""
    Results for T-Test between {col_1} and {col_2}:
    t-statistic: {t_stat}
    p-value: {p_val}
    """

def stddev(col: str, conversation_id: str) -> str:
    conversation = Conversation.objects.get(id=int(conversation_id))
    datasheet = conversation.conversation_datasheet
    df = pd.read_csv(datasheet.data_file)
    cols = list(df.columns)
    new_cols = [x.replace(' ', '_').lower() for x in cols]
    df = df.rename(columns=dict(zip(cols, new_cols)))
    col_name = col.replace(' ', '_').lower()
    if col_name not in new_cols:
        return "The provided column cannot be found in this datasheet."
    x = df[col_name].to_list()
    stddev = np.std(x)
    return f"""
    Results for the standard deviation of group with name {col}: {stddev}
    """

def simple_math_tool(expression: str) -> str:
    

    return f"""
    Results for the operation of {expression}: {eval(expression)}
    """

def run_calculations(prompt: str, conversation_id: str) -> str:
    """
    Create a data chain to answer data-related questions.

    Args:
        prompt (str): The question or prompt.
        df (pd.DataFrame): The dataframe containing the data.
        lib_name (str): The name of the library or datasheet.

    Returns:
        str: The synthesized answer to the prompt.
    """
    conversation = Conversation.objects.get(id=int(conversation_id))
    datasheet = conversation.conversation_datasheet
    df = pd.read_csv(datasheet.data_file)
    

    # accessed by duckdb
    cols = df.columns.tolist()
    new_cols = [x.replace(' ', '_').replace('/', '_').replace('-', '_').lower() for x in cols]
    input_table = df
    input_table.rename(columns=dict(zip(cols, new_cols)))
    numerical_columns = list(input_table.select_dtypes(include=['number']).columns)
    categorical_columns = list(input_table.select_dtypes(exclude=['number']).columns)

    formatted_numerical_cols = '\n'.join([f'{i + 1}. {x}' for i, x in enumerate(numerical_columns)])
    formatted_categorical_cols = '\n'.join([f'{i + 1}. {x}' for i, x in enumerate(categorical_columns)])
    
    sql_result = get_sql_code(prompt, formatted_numerical_cols, formatted_categorical_cols)
    print(sql_result)

    synthesis_prompt = f"""
You are a researcher that is given a small piece of data. Given a question and data, report the data and then answer the question using the data.
Example:
Question: What is the mean of A?
Data:
    mean_of_A
0      0.462
Answer: The data reflects that the mean of A is 0.462.

Your Turn:
Question: {prompt}
Data:
{sql_result}

Answer:
"""
    print(synthesis_prompt)
    return server_client.generate(MODEL, synthesis_prompt)['response']

# tool refs
def get_styling_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'style_component',
            'description': "Regenerate a plot to fit user styling suggestions",
            'parameters': {
                'type': 'object',
                'properties': {
                    'prompt': {
                        'type': 'string',
                        'description': 'The question or prompt',
                    },
                    'conversation_id': {
                        'type': 'string',
                        'description': 'The ID of the conversation',
                    },
                },
                'required': ['prompt', 'conversation_id'],
            },
        },
    }

def get_simple_math_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'simple_math_tool',
            'description': 'Perform a simple operation between two numbers (addition, subtraction, multiplication, division, exponentiation, or modulo)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'expression': {
                        'type': 'string',
                        'description': 'A mathematical expression that can be ran using python eval()',
                    }
                },
                'required': ['expression'],
            },
        }
    }
        
def get_ttest_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'ttest',
            'description': 'Perform an independent t-test on two lists of numbers',
            'parameters': {
                'type': 'object',
                'properties': {
                    'col_1': {
                        'type': 'string',
                        'description': 'Name of the first referenced column as a string',
                    },
                    'col_2': {
                        'type': 'string',
                        'description': 'Name of the second referenced column as a string',
                    },
                    'conversation_id': {
                        'type': 'string',
                        'description': 'The ID of the conversation',
                    },
                },
                'required': ['col_1', 'col_2', 'conversation_id'],
            },
        }
    }

def get_stddev_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'stddev',
            'description': 'Find the standard deviation for a set of values',
            'parameters': {
                'type': 'object',
                'properties': {
                    'col': {
                        'type': 'string',
                        'description': 'Name of the referenced column as a string',
                    },
                    'conversation_id': {
                        'type': 'string',
                        'description': 'The ID of the conversation',
                    },
                },
                'required': ['col', 'conversation_id'],
            },
        }
    }

def get_data_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'run_calculations',
            'description': 'Answer a question the requires calculations on data',
            'parameters': {
                'type': 'object',
                'properties': {
                    'prompt': {
                        'type': 'string',
                        'description': 'The question or prompt',
                    },
                    'conversation_id': {
                        'type': 'string',
                        'description': 'Numerical ID of the conversation',
                    },
                },
                'required': ['prompt', 'conversation_id'],
            },
        }
    }


def get_answer(prompt: str, conversation: Conversation, q_type: str) -> tuple:
    """
    Get an answer based on the question type and conversation history.

    Args:
        prompt (str): The question or prompt.
        conversation (Conversation): The conversation object.
        question_type (str): The type of question (STYLE or DATA).

    Returns:
        tuple: A tuple containing the prediction and any internal JSON.
    """

    internal_json = []

    messages = [{'role': 'system', 'content': f'This conversation has a conversation_id of {str(conversation.id)}. An external agent labeled the user content with the tag {q_type}.'},
                {'role': 'user', 'content': prompt}]

    # First API call: Send the query and function description to the model
    response = server_client.chat(
        model=MODEL,
        messages=messages,
        tools=[
            get_data_tool(),
            get_styling_tool(),
            get_ttest_tool(),
            get_stddev_tool(),
            get_simple_math_tool(),
        ]
    )

    # Add the model's response to the conversation history
    messages.append(response['message'])

    print('MESSAGES (pre-tool call): ', str(messages))

    # Process function calls made by the model
    if response['message'].get('tool_calls'):
        available_functions = {
        'run_calculations': run_calculations,
        'style_component': style_component,
        'ttest': ttest,
        'stddev': stddev,
        'simple_math_tool': simple_math_tool
        }
        for tool in response['message']['tool_calls']:
            function_to_call = available_functions[tool['function']['name']]
            function_response = function_to_call(**tool['function']['arguments'])

            if tool['function']['name'] == 'style_component':
                if '<JSON>' not in function_response or '</JSON>' not in function_response:
                    return function_response, []
                
                cleaned_response = function_response.replace('\n', '').replace(' ', '')
                print('cleaned response: ', cleaned_response)
                internal_json = cleaned_response[cleaned_response.rfind('<JSON>{')+6:cleaned_response.rfind('}</JSON>')+1]

                return function_response, internal_json

            # Add function response to the conversation
            messages.append(
                {
                'role': 'tool',
                'content': function_response,
                }
            )
    else:
        prediction = response['message']['content']
        print("The model didn't use the function. Its response was: ")
        print(prediction)
        return prediction, []

    # Second API call: Get final response from the model
    
    tools = []
    for message in messages:
        if message["role"] == "tool":
            tools.append(message["content"])

    tool_responses = '\n'.join(tools)
    print(tool_responses)
    

    instructions = f"""
    You will be given a user query as well as one or more tool responses.
    The answer to the user query will most likely be found in these tool responses, please formulate an answer based on the context found in the provided tool responses.
    Do not site these tool responses, answer if you had come up with the information in the responses yourself.

    Tool Responses:
    {tool_responses}

    Question: {prompt}
    """

    final_response = server_client.generate(MODEL, instructions)
    prediction = final_response['response'].replace('\n', '\\n')
    print(prediction)
    
    return prediction, internal_json

def get_question_type(question: str) -> dict:
    """
    Determine the type of question (STYLE or DATA).

    Args:
        question (str): The question to categorize.

    Returns:
        dict: A dictionary containing the question type.
    """

    prompt = f"""
    Categorize the following question as a STYLE question or a DATA question.
    Answer in JSON format. Surround the JSON by the tags <JSON> and </JSON>.
    STYLE questions involve changing things like color, size, or orientation, as if pertaining to a plot.
    DATA questions involve doing mathematical operations on data or pulling up associations and values from a data table.
    FORMAT: <JSON>{{"type": "STYLE" OR "DATA"}}</JSON>
    QUESTION: {question}
    ANSWER: """
    output = server_client.generate(MODEL, prompt)
    response: str = output['response'].replace('\n', '').replace(' ', '')
    print(response)
    if response.find('<JSON>') == -1 or response.find('</JSON>') == -1:
        print('no json tags found')
        return {"type": "none"}
    internal_json = response[response.find('<JSON>{')+6:response.find('}</JSON>')+1]
    print(internal_json)
    return json.loads(internal_json)