from django.core.management.base import BaseCommand, CommandError
from SEP.models import Employee, Role


class Command(BaseCommand):
    help = "Creates initial database entries for the SEP application"

    def handle(self, *args, **options):

        # Create initial roles
        for role_id, role_name in [
            ("CSE", "Customer Service Employee"),
            ("CSM", "Customer Service Manager"),
            ("FIM", "Financial Manager"),
            ("ADM", "Administration Dpt Manager")
        ]:
            _, created = Role.objects.get_or_create(id=role_id, name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Role {role_name} created."))
            else:
                self.stdout.write(self.style.WARNING(f"Role {role_name} already exists."))


        # Create initial employees
        if Employee.objects.get_or_create(
            username="cse1",
            first_name="Carmen",
            last_name="Santa-Emeritus",
            email="cse1@sep.se",
            role=Role.objects.get(id="CSE"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("CSE Employee Carmen Santa-Emeritus created."))
        else:
            self.stdout.write(self.style.WARNING("CSE Employee Carmen Santa-Emeritus already exists."))

        if Employee.objects.get_or_create(
            username="cse2",
            first_name="Cedric",
            last_name="Saladin-Ernandez",
            email="cse2@sep.se",
            role=Role.objects.get(id="CSE"),
        ):
            self.stdout.write(self.style.SUCCESS("CSE Employee Cedric Saladin-Ernandez created."))
        else:
            self.stdout.write(self.style.WARNING("CSE Employee Cedric Saladin-Ernandez already exists."))

        if Employee.objects.get_or_create(
            username="csm1",
            first_name="Carlos",
            last_name="Sitaro-Meritus",
            email="csm1@sep.se",
            role=Role.objects.get(id="CSM"),
        ):
            self.stdout.write(self.style.SUCCESS("CSM Employee Carlos Sitaro-Meritus created."))
        else:
            self.stdout.write(self.style.WARNING("CSM Employee Carlos Sitaro-Meritus already exists."))

        if Employee.objects.get_or_create(
            username="fim1",
            first_name="Fernando",
            last_name="Iniesta-Malan",
            email="fim1@sep.se",
            role=Role.objects.get(id="FIM"),
        ):
            self.stdout.write(self.style.SUCCESS("FIM Employee Fernando Iniesta-Malan created."))
        else:
            self.stdout.write(self.style.WARNING("FIM Employee Fernando Iniesta-Malan already exists."))

        if Employee.objects.get_or_create(
            username="adm1",
            first_name="Amanda",
            last_name="Dministrador",  # Thanks copilot
            email="adm1@sep.se",
            role=Role.objects.get(id="ADM"),
        ):
            self.stdout.write(self.style.SUCCESS("ADM Employee Amanda Dministrador created."))
        else:
            self.stdout.write(self.style.WARNING("ADM Employee Amanda Dministrador already exists."))

        for employee in Employee.objects.all():
            employee.set_password("1234")
            employee.save()
