from django.core.management.base import BaseCommand

from projects.models import Project, Skill
from users.models import User


class Command(BaseCommand):
    help = "Создает демонстрационных пользователей, проекты и навыки для ревью."

    def handle(self, *args, **options):
        demo_users = [
            {
                "email": "backend@example.com",
                "password": "demo-pass-123",
                "name": "Алина",
                "surname": "Серова",
                "phone": "+79990000001",
                "github_url": "https://github.com/backend-demo",
                "about": "Backend-разработчик, люблю API и аккуратные модели данных.",
            },
            {
                "email": "frontend@example.com",
                "password": "demo-pass-123",
                "name": "Марк",
                "surname": "Лебедев",
                "phone": "+79990000002",
                "github_url": "https://github.com/frontend-demo",
                "about": "Frontend-инженер, собираю интерфейсы для командных сервисов.",
            },
            {
                "email": "design@example.com",
                "password": "demo-pass-123",
                "name": "Нина",
                "surname": "Орлова",
                "phone": "+79990000003",
                "github_url": "https://github.com/design-demo",
                "about": "UX/UI-дизайнер, помогаю pet-проектам стать понятнее.",
            },
        ]

        users = []
        for user_data in demo_users:
            password = user_data["password"]
            defaults = user_data.copy()
            defaults.pop("password")

            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=defaults,
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)

        skill_names = ["Django", "PostgreSQL", "React", "UX Research", "Docker", "REST API"]
        skills = {}
        for skill_name in skill_names:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills[skill_name] = skill

        project_specs = [
            {
                "owner": users[0],
                "name": "SprintHub",
                "description": "Сервис для быстрых командных спринтов и распределения задач в pet-проектах.",
                "github_url": "https://github.com/backend-demo/sprinthub",
                "skills": ["Django", "PostgreSQL", "REST API"],
                "participants": [users[1]],
            },
            {
                "owner": users[1],
                "name": "Launch Desk",
                "description": "Панель подготовки релизов с чек-листами, ролями и историей запусков.",
                "github_url": "https://github.com/frontend-demo/launch-desk",
                "skills": ["React", "Docker", "REST API"],
                "participants": [users[0], users[2]],
            },
            {
                "owner": users[2],
                "name": "Persona Lab",
                "description": "Инструмент для хранения интервью, пользовательских сегментов и гипотез.",
                "github_url": "https://github.com/design-demo/persona-lab",
                "skills": ["UX Research", "React"],
                "participants": [users[1]],
            },
        ]

        for spec in project_specs:
            project, _ = Project.objects.get_or_create(
                owner=spec["owner"],
                name=spec["name"],
                defaults={
                    "description": spec["description"],
                    "github_url": spec["github_url"],
                    "status": Project.STATUS_OPEN,
                },
            )

            project.participants.add(spec["owner"])
            for participant in spec["participants"]:
                project.participants.add(participant)

            project_skills = []
            for skill_name in spec["skills"]:
                project_skills.append(skills[skill_name])
            project.skills.set(project_skills)

        self.stdout.write(self.style.SUCCESS("Демо-данные TeamFinder созданы или уже существуют."))
