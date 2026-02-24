"""Management command to run system health checks."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run system health checks (database, Redis, disk, memory)"

    def handle(self, *args, **options):
        import time

        self.stdout.write("Running system health checks...\n")

        # Database
        try:
            from django.db import connection
            start = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            ms = round((time.time() - start) * 1000, 2)
            self.stdout.write(self.style.SUCCESS(f"  Database: OK ({ms}ms)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Database: FAIL ({e})"))

        # Redis
        try:
            from django.core.cache import cache
            start = time.time()
            cache.set("health_check_cli", "ok", 10)
            val = cache.get("health_check_cli")
            ms = round((time.time() - start) * 1000, 2)
            if val == "ok":
                self.stdout.write(self.style.SUCCESS(f"  Redis: OK ({ms}ms)"))
            else:
                self.stdout.write(self.style.WARNING(f"  Redis: DEGRADED ({ms}ms)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Redis: FAIL ({e})"))

        # Celery
        try:
            from agentbloom.celery import app as celery_app
            i = celery_app.control.inspect()
            active = i.active()
            if active is not None:
                workers = len(active)
                self.stdout.write(self.style.SUCCESS(f"  Celery: OK ({workers} workers)"))
            else:
                self.stdout.write(self.style.WARNING("  Celery: No workers responding"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Celery: UNKNOWN ({e})"))

        # Disk
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            pct = round(used / total * 100, 1)
            free_gb = round(free / (1024**3), 1)
            if pct < 85:
                self.stdout.write(self.style.SUCCESS(f"  Disk: OK ({pct}% used, {free_gb}GB free)"))
            else:
                self.stdout.write(self.style.WARNING(f"  Disk: WARNING ({pct}% used, {free_gb}GB free)"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Disk: UNKNOWN ({e})"))

        # Migration check
        try:
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command("showmigrations", "--list", stdout=out)
            output = out.getvalue()
            unapplied = output.count("[ ]")
            if unapplied == 0:
                self.stdout.write(self.style.SUCCESS("  Migrations: All applied"))
            else:
                self.stdout.write(self.style.WARNING(f"  Migrations: {unapplied} unapplied"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Migrations: UNKNOWN ({e})"))

        self.stdout.write("\nHealth check complete.")
