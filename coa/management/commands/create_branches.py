# management/commands/create_branches.py
from django.core.management.base import BaseCommand
from coa.models import Branch

class Command(BaseCommand):
    help = 'Create initial branches'
    
    def handle(self, *args, **options):
        branches = [
            {'code': '01', 'name': 'Head Office - Accra', 'is_head_office': True},
            {'code': '02', 'name': 'Kumasi Main Branch', 'is_head_office': False},
            {'code': '03', 'name': 'Takoradi Branch', 'is_head_office': False},
            {'code': '04', 'name': 'Tamale Branch', 'is_head_office': False},
            {'code': '05', 'name': 'Cape Coast Branch', 'is_head_office': False},
        ]
        
        for branch_data in branches:
            branch, created = Branch.objects.get_or_create(
                code=branch_data['code'],
                defaults={
                    'name': branch_data['name'],
                    'is_head_office': branch_data['is_head_office']
                }
            )
            if created:
                self.stdout.write(f"Created branch: {branch.code} - {branch.name}")
        
        self.stdout.write(self.style.SUCCESS("Branches created successfully!"))