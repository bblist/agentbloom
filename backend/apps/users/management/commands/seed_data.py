"""Management command to seed initial data for development/staging."""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed initial data: superuser, demo org, feature flags, platform plans"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed data before re-creating",
        )

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial data...")

        self._create_superuser()
        org = self._create_demo_org()
        self._create_platform_plans()
        self._create_feature_flags()
        self._load_templates()

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    def _create_superuser(self):
        from apps.users.models import User

        if User.objects.filter(email="admin@agentbloom.com").exists():
            self.stdout.write("  Superuser already exists")
            return

        User.objects.create_superuser(
            email="admin@agentbloom.com",
            password="admin123!",
            full_name="AgentBloom Admin",
        )
        self.stdout.write(self.style.SUCCESS("  Created superuser: admin@agentbloom.com"))

    def _create_demo_org(self):
        from apps.users.models import User, Organization, OrgMember

        admin = User.objects.get(email="admin@agentbloom.com")

        org, created = Organization.objects.get_or_create(
            slug="demo",
            defaults={
                "name": "Demo Organization",
                "niche": "general",
                "owner": admin,
            },
        )
        if created:
            OrgMember.objects.get_or_create(
                org=org, user=admin,
                defaults={"role": "owner"},
            )
            self.stdout.write(self.style.SUCCESS("  Created demo organization"))
        else:
            self.stdout.write("  Demo organization already exists")

        return org

    def _create_platform_plans(self):
        from apps.payments.models import PlatformPlan

        plans = [
            {
                "name": "Free",
                "slug": "free",
                "price_monthly": 0,
                "price_yearly": 0,
                "features": {
                    "sites": 1,
                    "pages_per_site": 5,
                    "agent_chats_per_month": 50,
                    "contacts": 100,
                    "custom_domain": False,
                    "remove_branding": False,
                },
                "limits": {"sites": 1, "pages": 5, "contacts": 100},
                "sort_order": 0,
            },
            {
                "name": "Starter",
                "slug": "starter",
                "price_monthly": 29,
                "price_yearly": 290,
                "features": {
                    "sites": 3,
                    "pages_per_site": 20,
                    "agent_chats_per_month": 500,
                    "contacts": 1000,
                    "custom_domain": True,
                    "remove_branding": True,
                    "seo_tools": True,
                    "email_campaigns": True,
                },
                "limits": {"sites": 3, "pages": 20, "contacts": 1000},
                "sort_order": 1,
            },
            {
                "name": "Pro",
                "slug": "pro",
                "price_monthly": 79,
                "price_yearly": 790,
                "features": {
                    "sites": 10,
                    "pages_per_site": 100,
                    "agent_chats_per_month": 5000,
                    "contacts": 10000,
                    "custom_domain": True,
                    "remove_branding": True,
                    "seo_tools": True,
                    "email_campaigns": True,
                    "courses": True,
                    "bookings": True,
                    "payments": True,
                    "knowledge_base": True,
                },
                "limits": {"sites": 10, "pages": 100, "contacts": 10000},
                "sort_order": 2,
            },
            {
                "name": "Enterprise",
                "slug": "enterprise",
                "price_monthly": 249,
                "price_yearly": 2490,
                "features": {
                    "sites": -1,
                    "pages_per_site": -1,
                    "agent_chats_per_month": -1,
                    "contacts": -1,
                    "custom_domain": True,
                    "remove_branding": True,
                    "seo_tools": True,
                    "email_campaigns": True,
                    "courses": True,
                    "bookings": True,
                    "payments": True,
                    "knowledge_base": True,
                    "white_label": True,
                    "priority_support": True,
                    "api_access": True,
                },
                "limits": {"sites": -1, "pages": -1, "contacts": -1},
                "sort_order": 3,
            },
        ]

        for plan_data in plans:
            _, created = PlatformPlan.objects.update_or_create(
                slug=plan_data["slug"],
                defaults=plan_data,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status} plan: {plan_data['name']}")

    def _create_feature_flags(self):
        from apps.admin_panel.models import FeatureFlag

        flags = [
            ("ai_agent_enabled", True, "Enable AI agent chat feature"),
            ("course_builder_enabled", True, "Enable course builder"),
            ("booking_system_enabled", True, "Enable calendar booking"),
            ("email_campaigns_enabled", True, "Enable email campaign sending"),
            ("stripe_payments_enabled", True, "Enable Stripe payment processing"),
            ("seo_tools_enabled", True, "Enable SEO audit and keyword tracking"),
            ("knowledge_base_enabled", True, "Enable knowledge base and document processing"),
            ("webhooks_enabled", True, "Enable outgoing webhook delivery"),
            ("google_calendar_sync", False, "Enable Google Calendar synchronization"),
            ("white_label_mode", False, "Enable white-label branding"),
        ]

        for name, enabled, description in flags:
            _, created = FeatureFlag.objects.get_or_create(
                name=name,
                defaults={"is_enabled": enabled, "description": description},
            )
            if created:
                self.stdout.write(f"  Created flag: {name}")

    def _load_templates(self):
        from django.core.management import call_command

        try:
            call_command("loaddata", "initial_templates", verbosity=0)
            self.stdout.write(self.style.SUCCESS("  Loaded template fixtures"))
        except Exception as e:
            self.stdout.write(f"  Template fixture load skipped: {e}")
