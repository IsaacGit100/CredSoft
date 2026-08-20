from django.db import models

# Create your models here.

from django.db import models

# Create your models here.
# help_module/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models

class HelpCategory(models.Model):
    """Categories for help topics"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Help Categories"
    
    def __str__(self):
        return self.name
    
    





class HelpTopic(models.Model):
    """Individual help topics"""
    HELP_TYPES = [
        ('GENERAL', 'General'),
        ('HOW_TO', 'How To'),
        ('TROUBLESHOOT', 'Troubleshooting'),
        ('FAQ', 'FAQ'),
        ('GLOSSARY', 'Glossary'),
        ('VIDEO', 'Video Tutorial'),
    ]
    
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    help_type = models.CharField(max_length=20, choices=HELP_TYPES, default='GENERAL')
    
    # Related module (which module this help is for)
    module_name = models.CharField(max_length=50, blank=True, 
                                   choices=[
                                       ('SYSTEM_SETUP', 'System Setup'),
                                       ('USERS', 'Users'),
                                       ('MEMBERS', 'Members'),
                                       ('CHART_OF_ACCOUNTS', 'Chart of Accounts'),
                                       ('LOANS', 'Loans'),
                                       ('RECEIPTS_PAYMENTS', 'Receipts and Payments'),
                                       ('FINANCE', 'Finance'),
                                       ('INVESTMENTS', 'Investments'),
                                   ])
    
    # Keywords for search
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_help_topics')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_help_topics')
    updated_date = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_featured', 'title']
    
    def __str__(self):
        return self.title
    
    @property
    def module_display(self):
        return dict(self._meta.get_field('module_name').choices).get(self.module_name, 'General')

class HelpArticle(models.Model):
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='articles', default=None)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default=None)
    content = models.TextField()
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    """Detailed help articles"""
    topic = models.ForeignKey(HelpTopic, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
    
class HelpSearch(models.Model):
    """Track user searches for analytics"""
    search_term = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    search_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-search_date']

class HelpFeedback(models.Model):
    """User feedback on help content"""
    help_topic = models.ForeignKey(HelpTopic, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    was_helpful = models.BooleanField(null=True)
    comment = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']

class UserGuide(models.Model):
    """User guides and manuals"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    content = models.TextField()
    pdf_file = models.FileField(upload_to='help_guides/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='help_covers/', blank=True, null=True)
    
    # For which module
    module_name = models.CharField(max_length=50, blank=True, 
                                   choices=[
                                       ('SYSTEM_SETUP', 'System Setup'),
                                       ('USERS', 'Users'),
                                       ('MEMBERS', 'Members'),
                                       ('CHART_OF_ACCOUNTS', 'Chart of Accounts'),
                                       ('LOANS', 'Loans'),
                                       ('RECEIPTS_PAYMENTS', 'Receipts and Payments'),
                                       ('FINANCE', 'Finance'),
                                       ('INVESTMENTS', 'Investments'),
                                   ])
    
    version = models.CharField(max_length=20, default='1.0')
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_guides')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title