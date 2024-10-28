from django.contrib import admin
from django.urls import path, include

import SEP.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', views.home, name="home"),
    path('employee/', views.employee_home, name="employee_home"),
    path('project/', include("project.urls", namespace="project")),
]
