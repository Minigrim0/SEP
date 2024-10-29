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
]
