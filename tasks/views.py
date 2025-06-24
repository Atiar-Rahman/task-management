from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from tasks.forms import TaskForm,TaskModelForm
from tasks.models import Employee,Task
def Home(request):
    return HttpResponse('hekko')

def showTask(request):
    return HttpResponse('show all task')

def showSpecific_task(request,id):
    return HttpResponse(f"this is specific task page: {id}")

def Manager_Dashboard(request):
    return render(request,'dashboard/manager_dashboard.html')
def User_Dashboard(request):
    return render(request,'dashboard/user_dashboard.html')


# def create_task(request):
#     employees = Employee.objects.all()
#     form = TaskForm(employees=employees)
#     if request.method=='POST':
#         form = TaskForm(request.POST,employees=employees)
#         if form.is_valid():
#             print(form.cleaned_data)
#             data = form.cleaned_data
#             title = data.get('title')
#             description = data.get('description')
#             due_date = data.get('due_date')
#             assigned_to = data.get('assigned_to')#list[]

#             task = Task.objects.create(title=title,description=description,due_date=due_date)

#             #assign employee to task
#             for emp_id in assigned_to:
#                 employee = Employee.objects.get(id=emp_id)
#                 task.assigned_to.add(employee)
            
#             return HttpResponse("task added successfully")
#     context = {"form":form}
#     return render(request,'task_form.html',context)
def create_task(request):
    employees = Employee.objects.all()
    form = TaskModelForm() # for get
    if request.method=='POST':
        form = TaskModelForm(request.POST)
        if form.is_valid():
            form.save() 
            return HttpResponse("task added successfully")
    context = {"form":form}
    return render(request,'task_form.html',context)