# management/commands/init_help_content.py
from django.core.management.base import BaseCommand
from help_module.models import HelpCategory, HelpTopic, HelpArticle, UserGuide

class Command(BaseCommand):
    help = 'Initialize help content for all modules'
    
    def handle(self, *args, **options):
        # Create categories
        categories = [
            {'name': 'Getting Started', 'slug': 'getting-started', 'icon': 'rocket', 'order': 1},
            {'name': 'Members Management', 'slug': 'members', 'icon': 'users', 'order': 2},
            {'name': 'Loan Operations', 'slug': 'loans', 'icon': 'hand-holding-usd', 'order': 3},
            {'name': 'Accounting & Finance', 'slug': 'finance', 'icon': 'chart-line', 'order': 4},
            {'name': 'Investments', 'slug': 'investments', 'icon': 'chart-pie', 'order': 5},
            {'name': 'System Administration', 'slug': 'system', 'icon': 'cogs', 'order': 6},
            {'name': 'Troubleshooting', 'slug': 'troubleshooting', 'icon': 'wrench', 'order': 7},
        ]
        
        for cat_data in categories:
            HelpCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
        
        # Create help topics for each module
        topics = [
            # System Setup
            {
                'category': 'system',
                'title': 'How to Configure System Settings',
                'slug': 'configure-system-settings',
                'content': 'Step-by-step guide to configure system settings...',
                'help_type': 'HOW_TO',
                'module_name': 'SYSTEM_SETUP',
                'keywords': 'settings, configuration, system setup'
            },
            {
                'category': 'system',
                'title': 'User Management and Permissions',
                'slug': 'user-management',
                'content': 'Learn how to create users and assign permissions...',
                'help_type': 'HOW_TO',
                'module_name': 'USERS',
                'keywords': 'users, roles, permissions, access control'
            },
            
            # Members
            {
                'category': 'members',
                'title': 'Adding New Members',
                'slug': 'add-new-members',
                'content': 'Complete guide to registering new members...',
                'help_type': 'HOW_TO',
                'module_name': 'MEMBERS',
                'keywords': 'add member, register, new member'
            },
            {
                'category': 'members',
                'title': 'Managing Member Accounts',
                'slug': 'manage-member-accounts',
                'content': 'How to update member information and manage accounts...',
                'help_type': 'HOW_TO',
                'module_name': 'MEMBERS',
                'keywords': 'update member, edit member, account management'
            },
            {
                'category': 'members',
                'title': 'Member FAQs',
                'slug': 'member-faqs',
                'content': 'Frequently asked questions about members...',
                'help_type': 'FAQ',
                'module_name': 'MEMBERS',
                'keywords': 'faq, questions, answers'
            },
            
            # Chart of Accounts
            {
                'category': 'finance',
                'title': 'Setting Up Chart of Accounts',
                'slug': 'setup-chart-of-accounts',
                'content': 'Learn how to configure your chart of accounts...',
                'help_type': 'HOW_TO',
                'module_name': 'CHART_OF_ACCOUNTS',
                'keywords': 'accounts, chart of accounts, GL accounts'
            },
            {
                'category': 'finance',
                'title': 'Posting Journal Entries',
                'slug': 'post-journal-entries',
                'content': 'Step-by-step guide to posting journal entries...',
                'help_type': 'HOW_TO',
                'module_name': 'CHART_OF_ACCOUNTS',
                'keywords': 'journal entries, debits, credits, posting'
            },
            
            # Loans
            {
                'category': 'loans',
                'title': 'Loan Application Process',
                'slug': 'loan-application-process',
                'content': 'Complete guide to processing loan applications...',
                'help_type': 'HOW_TO',
                'module_name': 'LOANS',
                'keywords': 'loan application, apply loan, process loan'
            },
            {
                'category': 'loans',
                'title': 'Adding Guarantors to Loans',
                'slug': 'add-loan-guarantors',
                'content': 'How to add and manage loan guarantors...',
                'help_type': 'HOW_TO',
                'module_name': 'LOANS',
                'keywords': 'guarantors, sureties, loan guarantees'
            },
            {
                'category': 'loans',
                'title': 'Loan Repayment and Release of Guarantors',
                'slug': 'loan-repayment',
                'content': 'Learn how payments release guarantors...',
                'help_type': 'HOW_TO',
                'module_name': 'LOANS',
                'keywords': 'repayment, payment, release guarantor'
            },
            {
                'category': 'loans',
                'title': 'Common Loan Issues',
                'slug': 'loan-troubleshooting',
                'content': 'Troubleshooting common loan problems...',
                'help_type': 'TROUBLESHOOT',
                'module_name': 'LOANS',
                'keywords': 'error, problem, issue, troubleshooting'
            },
            
            # Receipts and Payments
            {
                'category': 'finance',
                'title': 'Processing Receipts',
                'slug': 'process-receipts',
                'content': 'How to record member payments and receipts...',
                'help_type': 'HOW_TO',
                'module_name': 'RECEIPTS_PAYMENTS',
                'keywords': 'receipts, payments, cash receipts'
            },
            {
                'category': 'finance',
                'title': 'Payment Methods and Types',
                'slug': 'payment-methods',
                'content': 'Guide to different payment methods (Cash, Cheque, Transfer)...',
                'help_type': 'HOW_TO',
                'module_name': 'RECEIPTS_PAYMENTS',
                'keywords': 'payment methods, cash, cheque, transfer, momo'
            },
            
            # Finance
            {
                'category': 'finance',
                'title': 'Generating Financial Reports',
                'slug': 'generate-reports',
                'content': 'How to generate and interpret financial reports...',
                'help_type': 'HOW_TO',
                'module_name': 'FINANCE',
                'keywords': 'reports, financial statements, trial balance'
            },
            {
                'category': 'finance',
                'title': 'Month-End Closing Procedures',
                'slug': 'month-end-closing',
                'content': 'Step-by-step month-end closing process...',
                'help_type': 'HOW_TO',
                'module_name': 'FINANCE',
                'keywords': 'month-end, closing, reconciliation'
            },
            
            # Investments
            {
                'category': 'investments',
                'title': 'Investment Types and Options',
                'slug': 'investment-types',
                'content': 'Overview of available investment options...',
                'help_type': 'GENERAL',
                'module_name': 'INVESTMENTS',
                'keywords': 'investments, treasury bills, bonds, fixed deposits'
            },
            {
                'category': 'investments',
                'title': 'Recording Investment Returns',
                'slug': 'record-investment-returns',
                'content': 'How to record interest and dividends from investments...',
                'help_type': 'HOW_TO',
                'module_name': 'INVESTMENTS',
                'keywords': 'returns, interest, dividends, investment income'
            },
        ]
        
        for topic_data in topics:
            category = HelpCategory.objects.get(slug=topic_data.pop('category'))
            HelpTopic.objects.get_or_create(
                slug=topic_data['slug'],
                defaults={**topic_data, 'category': category}
            )
        
        self.stdout.write(self.style.SUCCESS("Help content initialized successfully!"))