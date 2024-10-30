from django.urls import path

import project.views as views

app_name = "project"
urlpatterns = [
    path('', views.project_list, name="project_list"),                                      # View for a list of all projects
    path('<int:project_id>', views.project_detail, name="project_detail"),                  # View for the detail of a project
    path('from-raw/<int:id>', views.create_project_from_raw, name="project_from_raw"),      # View for the CS employee to format a request into a potential project
    path('<int:project_id>/csm-action', views.csm_action, name="csm_action"),               # View for the CSM to approve/reject a project
    path('<int:project_id>/fin-action', views.fin_action, name="fin_action"),               # View for the Finance Manager to write feedback on the project
    path('<int:project_id>/adm-action', views.adm_action, name="adm_action"),  # View for the Admin to approve/reject a project
    path('<int:project_id>/psdm-action', views.psdm_action, name="psdm_action"),  # View for the P/SDM to navigate to tasks assignment per team
    path('<int:project_id>/psdm-action/<int:team_id>/', views.psdm_team_action, name="psdm_team_action"),  # View for the P/SDM to assign tasks to a team's members
    path('<int:project_id>/tasks/<int:task_id>', views.task_detail, name="task_detail")
]
