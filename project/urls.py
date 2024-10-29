from django.urls import path

import project.views as views

app_name = "project"
urlpatterns = [
    path('<int:project_id>', views.project_detail, name="project_detail"),             # View for the detail of a project
    path('from-raw/<int:id>', views.create_project_from_raw, name="project_from_raw"),    # View for the CS employee to format a request into a potential project
    path('<int:id>/csm-action', views.create_project_from_raw, name="csm_action"),  # View for the CSM to approve/reject a project
    path('<int:id>/fin-action', views.create_project_from_raw, name="fin_action"),  # View for the Finance Manager to write feedback on the project
    path('<int:id>/adm-action', views.create_project_from_raw, name="adm_action"),  # View for the Admin to approve/reject a project
]
