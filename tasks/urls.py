
from django.urls import path
from tasks.views import showTask,showSpecific_task,Manager_Dashboard,User_Dashboard

urlpatterns = [
    path('show-task/',showTask), 
    path('show-task/<int:id>',showSpecific_task),
    path('manager-dashboard/',Manager_Dashboard),
    path('user-dashboard/',User_Dashboard)   
]
