from django.core.management.base import BaseCommand, CommandError
from SEP.models import Employee, Role, Team


class Command(BaseCommand):
    help = "Creates initial database entries for the SEP application"

    def handle(self, *args, **options):

        # Create initial roles
        for role_id, role_name in [
            ("CSE", "Customer Service Employee"),
            ("CSM", "Customer Service Manager"),
            ("FIM", "Financial Manager"),
            ("ADM", "Administration Dpt Manager"),
            ("PDE", "Production Dpt Manager"),
            ("PDM", "Production Dpt Employee"),
            ("SDE", "Service Dpt Manager"),
            ("SDM", "Service Dpt Employee"),
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
        )[1]:
            self.stdout.write(self.style.SUCCESS("CSE Employee Cedric Saladin-Ernandez created."))
        else:
            self.stdout.write(self.style.WARNING("CSE Employee Cedric Saladin-Ernandez already exists."))

        if Employee.objects.get_or_create(
            username="csm1",
            first_name="Carlos",
            last_name="Sitaro-Meritus",
            email="csm1@sep.se",
            role=Role.objects.get(id="CSM"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("CSM Employee Carlos Sitaro-Meritus created."))
        else:
            self.stdout.write(self.style.WARNING("CSM Employee Carlos Sitaro-Meritus already exists."))

        if Employee.objects.get_or_create(
            username="fim1",
            first_name="Fernando",
            last_name="Iniesta-Malan",
            email="fim1@sep.se",
            role=Role.objects.get(id="FIM"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("FIM Employee Fernando Iniesta-Malan created."))
        else:
            self.stdout.write(self.style.WARNING("FIM Employee Fernando Iniesta-Malan already exists."))

        if Employee.objects.get_or_create(
            username="adm1",
            first_name="Amanda",
            last_name="Dministrador",  # Thanks copilot
            email="adm1@sep.se",
            role=Role.objects.get(id="ADM"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("ADM Employee Amanda Dministrador created."))
        else:
            self.stdout.write(self.style.WARNING("ADM Employee Amanda Dministrador already exists."))

        if Employee.objects.get_or_create(
            username="pdm1",
            first_name="Patrik",
            last_name="De Mager",
            email="pdm1@sep.se",
            role=Role.objects.get(id="PDM"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("PDM Employee Patrik De Mager created."))
        else:
            self.stdout.write(self.style.WARNING("PDM Employee Patrik De Mager already exists."))

        if Employee.objects.get_or_create(
            username="sdm1",
            first_name="Sara",
            last_name="Du Mer",
            email="sdm1@sep.se",
            role=Role.objects.get(id="SDM"),
        )[1]:
            self.stdout.write(self.style.SUCCESS("SDM Employee Sara Du Mer created."))
        else:
            self.stdout.write(self.style.WARNING("SDM Employee Sara Du Mer already exists."))

        # Producttion teams under the production manager
        for team in [
            "photographers",
            "audio",
            "graphic",
            "decoration",
            "network"
        ]:
            _, created = Team.objects.get_or_create(
                name=team,
                manager=Employee.objects.get(username="pdm1"),
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Team {team.capitalize()} created."))
            else:
                self.stdout.write(self.style.WARNING(f"Team {team.capitalize()} already exists."))

        # Service teams under the service manager
        for team in [
            "Cook",
            "Waiter"
        ]:
            _, created = Team.objects.get_or_create(
                name=team,
                manager=Employee.objects.get(username="sdm1"),
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Team {team.capitalize()} created."))
            else:
                self.stdout.write(self.style.WARNING(f"Team {team.capitalize()} already exists."))

        # Create some employees for the production teams
        for team in Team.objects.filter(manager=Employee.objects.get(username="pdm1")):
            for i in range(1, 4):
                employee, created = Employee.objects.get_or_create(
                    username=f"{team.name}{i}",
                    first_name=f"{team.name.capitalize()}",
                    last_name=f"{i}",
                    email=f"{team.name}{i}@sep.se",
                    role=Role.objects.get(id="PDM"),
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"{team.name.capitalize()} {i} created."))
                else:
                    self.stdout.write(self.style.WARNING(f"{team.name.capitalize()} {i} already exists."))

                self.stdout.write(self.style.SUCCESS(f"Connecting {employee.username} to team {team.name}"))
                team.members.add(employee)

        # Create some employees for the service teams
        for team in Team.objects.filter(manager=Employee.objects.get(username="sdm1")):
            for i in range(1, 4):
                employee, created = Employee.objects.get_or_create(
                    username=f"{team.name}{i}",
                    first_name=f"{team.name.capitalize()}",
                    last_name=f"{i}",
                    email=f"{team.name}{i}@sep/.se",
                    role=Role.objects.get(id="SDM"),
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"{team.name.capitalize()} {i} created."))
                else:
                    self.stdout.write(self.style.WARNING(f"{team.name.capitalize()} {i} already exists."))

                self.stdout.write(self.style.SUCCESS(f"Connecting {employee.username} to team {team.name}"))
                team.members.add(employee)

        for employee in Employee.objects.all():
            employee.set_password("1234")
            employee.save()
