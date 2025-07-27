from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Task, TaskDetail, Project
from datetime import date
from django.db.models import Q, Count, Max, Min, Avg
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from users.views import is_admin
from django.views import View
from django.views.generic.edit import CreateView,UpdateView,DeleteView,ListView
from django.urls import reverse_lazy


# Create your views here.
def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_employee(user):
    return user.groups.filter(name='Manager').exists()


@user_passes_test(is_manager, login_url='no-permission')
def manager_dashboard(request):

    # getting task count
    # total_task = tasks.count()
    # completed_task = Task.objects.filter(status="COMPLETED").count()
    # in_progress_task = Task.objects.filter(status='IN_PROGRESS').count()
    # pending_task = Task.objects.filter(status="PENDING").count()

    # count = {
    #     "total_task":
    #     "completed_task":
    #     "in_progress_task":
    #     "pending_task":
    # }
    type = request.GET.get('type', 'all')
    # print(type)

    counts = Task.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='COMPLETED')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        pending=Count('id', filter=Q(status='PENDING')),
    )

    # Retriving task data

    base_query = Task.objects.select_related(
        'details').prefetch_related('assigned_to')

    if type == 'completed':
        tasks = base_query.filter(status='COMPLETED')
    elif type == 'in-progress':
        tasks = base_query.filter(status='IN_PROGRESS')
    elif type == 'pending':
        tasks = base_query.filter(status='PENDING')
    elif type == 'all':
        tasks = base_query.all()

    context = {
        "tasks": tasks,
        "counts": counts,
        "role": 'manager'
    }
    return render(request, "dashboard/manager-dashboard.html", context)


@user_passes_test(is_employee)
def employee_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


@login_required
@permission_required("tasks.add_task", login_url='no-permission')
def create_task(request):
    # employees = Employee.objects.all()
    task_form = TaskModelForm()  # For GET
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Created Successfully")
            return redirect('create-task')

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)

# class based view for 
class CreateTask(View):
    """View for creating a Task and associated TaskDetail"""
    template_name = "task_form.html"

    def get(self, request, *args, **kwargs):
        task_form = TaskModelForm()
        task_detail_form = TaskDetailModelForm()
        context = {
            "task_form": task_form,
            "task_detail_form": task_detail_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            # Save Task first, using commit=False so we can handle M2M and related models
            task = task_form.save(commit=False)

            # Optional: ensure project exists to avoid foreign key errors
            if not task.project_id:
                default_project = Project.objects.first()
                if default_project:
                    task.project = default_project
                else:
                    messages.error(request, "❌ No project exists. Please create a project first.")
                    return redirect('create-task')

            task.save()
            task_form.save_m2m()  # Save assigned_to many-to-many relationship

            # Save TaskDetail
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "✅ Task Created Successfully")
            return redirect('create-task')

        # If not valid, return form with errors
        messages.error(request, "⚠️ Please correct the errors below.")
        context = {
            "task_form": task_form,
            "task_detail_form": task_detail_form
        }
        return render(request, self.template_name, context)


# class CreateTaskView1(CreateView):
#     template_name = 'task_form1.html'
#     form_class = TaskModelForm

#     def get_context_data(self, **kwargs):
#         print(**kwargs)
#         context = super().get_context_data(**kwargs)
#         context['task_form'] = kwargs.get('task_form',TaskModelForm())
#         # context['task_detail_form'] = TaskDetailModelForm
#         return context
    

#     def get(self,request,*args, **kwargs):
#         context = self.get_context_data()
#         print(context)
#         return render(request,self.template_name,context) 
        
#     def post(self,request,*args,**kwargs):
#         pass
class CreateTaskView1(CreateView):
    # model = Task
    form_class = TaskModelForm
    template_name = 'task_form1.html'
    success_url = reverse_lazy('task-list')  # Change to your success page
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = kwargs.get('task_form', TaskModelForm())
        context['task_detail_form'] = kwargs.get('task_detail_form', TaskDetailModelForm())
        return context


    def get(self, request, *args, **kwargs):
        """Handles GET request and renders both forms."""
        self.object = None
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handles POST request and processes both forms."""
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()
            messages.success(request, "Task and details created successfully")
            return super().form_valid(task_form)  # Redirect to success_url

        # If form is invalid, re-render with errors
        context = self.get_context_data(task_form=task_form, task_detail_form=task_detail_form)
        return render(request, self.template_name, context)

@login_required
@permission_required("tasks.change_task", login_url='no-permission')
def update_task(request, id):
    task = Task.objects.get(id=id)
    task_form = TaskModelForm(instance=task)  # For GET

    if task.details:
        task_detail_form = TaskDetailModelForm(instance=task.details)

    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(
            request.POST, instance=task.details)

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', id)

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)

# update task used classbased view
class UpdateTask(View):
    template_name = "task_form.html"
    def get(self,request,id,*args,**kwargs):
        task = Task.objects.get(id=id)
        task_form = TaskModelForm(instance=task)  # For GET
        if task.details:
            task_detail_form = TaskDetailModelForm(instance=task.details)
        else:
            task_detail_form = TaskDetailModelForm()
        
        context = {"task_form": task_form, 
                   "task_detail_form": task_detail_form
                   }
        return render(request, self.template_name, context)

       
    def post(self,request,id,*args,**kwargs):
        task = Task.objects.get(id=id)
        
        task_form = TaskModelForm(request.POST,instance = task)
        task_detail_form = TaskDetailModelForm(request.POST,instance = task)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', id=id)
        
        context = {
            "task_form": task_form,
            "task_detail_form": task_detail_form
        }
        return render(request, self.template_name, context)




class UpdateTask1(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form1.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        
        if hasattr(self.object,'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(instance = self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()
        return context
    
    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST,instance=self.object)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES,instance=getattr(self.object,'details',None))

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task= task
            task_detail.save()

            return redirect('update-task',self.object.id)
        return self.render_to_response(self.get_context_data(
            task_form=task_form,
            task_detail_form=task_detail_form
        ))


@login_required
@permission_required("tasks.delete_task", login_url='no-permission')
def delete_task(request, id):
    if request.method == 'POST':
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, 'Task Deleted Successfully')
        return redirect('manager-dashboard')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('manager-dashboard')

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'  # Optional: your confirmation template
    pk_url_kwarg = 'id'  # Use 'id' instead of default 'pk'
    success_url = reverse_lazy('manager-dashboard')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Task Deleted Successfully')
        return super().post(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, 'Something went wrong')
        return redirect('manager-dashboard')

@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def view_task(request):
    projects = Project.objects.annotate(
        num_task=Count('task')).order_by('num_task')
    return render(request, "show_task.html", {"projects": projects})


class TaskSummaryView(ListView):
    model = Project
    template_name = 'show_task.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.annotate(num_task=Count('task')).order_by('num_task')

@login_required
@permission_required("tasks.view_task", login_url='no-permission')
def task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    status_choices = Task.STATUS_CHOICES

    if request.method == 'POST':
        selected_status = request.POST.get('task_status')
        print(selected_status)
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)

    return render(request, 'task_details.html', {"task": task, 'status_choices': status_choices})

class TaskDetailView(View):
    template_name = 'task_details.html'
    pk_url_kwarg = 'task_id'
    def get(self, request, task_id, *args, **kwargs):
        task = Task.objects.get(id=task_id)
        status_choices = Task.STATUS_CHOICES
        return render(request, self.template_name, {
            'task': task,
            'status_choices': status_choices
        })

    def post(self, request, task_id, *args, **kwargs):
        task = Task.objects.get(id = task_id)
        selected_status = request.POST.get('task_status')
        task.status = selected_status
        task.save()
        return redirect('task-details', task.id)
    
@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')

    return redirect('no-permission')