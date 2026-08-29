from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import HelpCategory, HelpArticle

@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'order']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}