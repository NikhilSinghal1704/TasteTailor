from django.contrib import admin
from .models import *
from .models import PantryItem

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


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "calories", "protein", "carbohydrates", "fat")
    list_filter = ("date",)
    search_fields = ("user__username",)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("plan", "meal_type", "title", "ready_in_minutes", "servings")
    list_filter = ("meal_type",)
    search_fields = ("title",)


@admin.register(GeneratedRecipe)
class GeneratedRecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at", "diet_type")
    list_filter = ("diet_type", "created_at")
    search_fields = ("user__username", "title", "prompt")


@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "spoonacular_id", "created_at")
    list_filter = ("user",)
    search_fields = ("name", "user__username")
