# Local imports
from ..models import List, Task, Attachment

def update_tasklist(name, category, labels, dates, task_ids):
    
    if List.objects.filter(name = name, category = category).exists():
        tasklist = List.objects.get(name = name, category = category)
    else:
        tasklist = List.objects.create(name = name, category = category, user = 'test')
        
    for label, date, task_id in zip(labels, dates, task_ids):
        print("creating ", label)
        if Task.objects.filter(task_iden = str(task_id)).exists():
            current_task = Task.objects.get(task_iden = str(task_id))
            current_task.title = label
            current_task.due_date = date
            current_task.save()
        else:
            Task.objects.create(task_iden = str(task_id), title = label, due_date = date, tasklist = tasklist)
        print(label, ' saved to list ', name)