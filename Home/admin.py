from django.contrib import admin
from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'email', 'is_active', 'rotation_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('key', 'email')
    list_editable = ('is_active', 'rotation_order')

admin.site.site_header = 'API Key Administration'
