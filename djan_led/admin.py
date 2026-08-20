from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    list_filter = ('default_entity',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('allowed_entities',)
    
   