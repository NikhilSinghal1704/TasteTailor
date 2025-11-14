from django.contrib import admin
from .models import UserPreferences

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'height_cm', 'weight_kg', 'goal', 'preferences_completed', 'created_at')
    list_filter = ('goal', 'activity_level', 'cooking_skill', 'preferences_completed', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'bio')
        }),
        ('Physical Information', {
            'fields': ('height_cm', 'weight_kg', 'target_weight_kg')
        }),
        ('Health & Fitness', {
            'fields': ('goal', 'activity_level', 'daily_calorie_target')
        }),
        ('Dietary Preferences', {
            'fields': ('diet_type', 'preferred_cuisines', 'cooking_skill', 'average_cooking_time', 'kitchen_equipment')
        }),
        ('Allergies & Intolerances', {
            'fields': ('allergies', 'intolerances')
        }),
        ('Ingredients', {
            'fields': ('favorite_ingredients', 'disliked_ingredients')
        }),
        ('Budget & Preferences', {
            'fields': ('budget_preference', 'spice_level', 'prefer_simple_recipes', 'prefer_healthy')
        }),
        ('Health Conditions', {
            'fields': ('diabetes', 'hypertension', 'celiac', 'lactose_intolerant', 'heart_disease', 'other_conditions')
        }),
        ('Lifestyle', {
            'fields': ('meals_per_day', 'prefer_meal_prep', 'meal_prep_frequency')
        }),
        ('Recipe Preferences', {
            'fields': ('min_recipe_rating',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'preferences_completed'),
            'classes': ('collapse',)
        })
    )

