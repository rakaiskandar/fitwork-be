import json
from django.core.management.base import BaseCommand
from api.companies.models import Company

class Command(BaseCommand):
    help = "Import company EVP data from JSON file"

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Path to evp_knowledge.json')

    def handle(self, *args, **kwargs):
        path = kwargs['json_path']
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        count = 0
        for entry in data:
            company, created = Company.objects.get_or_create(
                name=entry["company_name"],
                defaults={
                    "career_url": entry.get("career_url"),
                    "mission_statement": entry.get("mission_statement"),
                    "core_values": entry.get("core_values", []),
                    "culture_keywords": entry.get("culture_keywords", [])
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} new companies."))
