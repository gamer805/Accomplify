# Local imports
from ..models import List, Task, Attachment, AccomplifyUser

def update_tasklist(name, category, user, labels, dates, task_ids):
    
    if List.objects.filter(name = name, category = category).exists():
        tasklist = List.objects.get(name = name, category = category)
    else:
        tasklist = List.objects.create(name = name, category = category, user = user)
        
    for label, date, task_id in zip(labels, dates, task_ids):
        print("creating ", label)
        if Task.objects.filter(task_iden = str(task_id)).exists():
            current_task = Task.objects.get(task_iden = str(task_id))
            current_task.title = label
            current_task.due_date = date
            current_task.user = user
            current_task.save()
        else:
            Task.objects.create(task_iden = str(task_id), title = label, due_date = date, tasklist = tasklist, user = user)
        print(label, ' saved to list ', name)
        
def collect_tasklist(user):
    tasklists = List.objects.filter(user = user)
    task_collection = {}
    for tasklist in tasklists:
        category = tasklist.category + '-' + tasklist.name
        tasks = Task.objects.filter(user = user, tasklist = tasklist)
        tasks_per_cat = []
        for task in tasks:
            tasks_per_cat.append({"id": '', "label": task.title, "date": task.due_date, "completed": task.completed})
        task_collection[category] = tasks_per_cat
    return task_collection
    