from django.db import models

# Create your models here.
class Task(models.Model):
    # project = models.models.ForeignKey("Project",on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField()
    dudate = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # one to one
    # many to one
    # many to many

class TaskDetails(models.Model):

    HIGH='H'
    MEDIUM='M'
    LOW='L'

    PRIOITY_OPTIONS = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low')
    )
    task = models.OneToOneField(Task,on_delete=models.CASCADE)
    assign_to = models.CharField(max_length=100)
    priority = models.CharField(max_length=1,choices=PRIOITY_OPTIONS,default=LOW)




#  Task.objects.get(id=2)
# select * from task wjere id = 2
# orm = object relation mapping

class Project(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
