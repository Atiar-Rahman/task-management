
from django.urls import path
from tasks.views import showTask,showSpecific_task

urlpatterns = [
    path('show-task/',showTask), 
    path('show-task/<int:id>',showSpecific_task)   
]
