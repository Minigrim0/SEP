from django.contrib import admin

from SEP.models import Customer, Employee, Team, TeamToEmployee

class TeamMemberInline(admin.TabularInline):
    model = TeamToEmployee
    list_display = ("employee", "is_chief")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "role")
    list_filter = ("role",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", )
    inlines = (TeamMemberInline, )
