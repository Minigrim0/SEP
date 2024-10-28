from django.contrib import admin

from project.models import Project, RawRequest, Meeting


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "status")
    list_filter = ("status",)
    search_fields = ("title", "client__name")


@admin.register(RawRequest)
class RawRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("date", "time")
    search_fields = ("date", "time")
