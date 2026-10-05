# RecPayApp/management/commands/repair_trans_pk.py

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset the AUTO_INCREMENT counter on recpayapp_trans if it has drifted."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM recpayapp_trans;")
            max_id = cursor.fetchone()[0] or 0
            next_id = max_id + 1
            cursor.execute(f"ALTER TABLE recpayapp_trans AUTO_INCREMENT = {next_id};")
            self.stdout.write(
                self.style.SUCCESS(
                    f"AUTO_INCREMENT on recpayapp_trans set to {next_id} (max id was {max_id})."
                )
            )
