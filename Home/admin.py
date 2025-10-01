from django.contrib import admin
from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'usage_count')
    list_filter = ('is_active', 'usage_count', 'last_called')
    search_fields = ('key', 'email')
    list_editable = ('is_active',)

    add_fieldsets = (
        ("Details", {
            'fields': ('key', 'email', 'is_active')
        }),
    )
    
    fieldsets = (
        ("Details", {
            'fields': ('key', 'email', 'is_active', 'usage_count')
        }),
        ('Date Information', {
            'fields': ('call_history', 'last_called', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

admin.site.site_header = 'TasteTailor Administration'
