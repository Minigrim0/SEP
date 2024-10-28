from django.urls import path

import project.views as views

app_name = "project"
urlpatterns = [
    path('from-raw/<int:id>', views.create_project_from_raw, name="project_from_raw"),
]
