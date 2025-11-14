from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserPreferences(models.Model):
    """
    Extended user preferences for personalized recipe recommendations
    """
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (Little or no exercise)'),
        ('light', 'Light (Exercise 1-3 days/week)'),
        ('moderate', 'Moderate (Exercise 3-5 days/week)'),
        ('very_active', 'Very Active (Exercise 6-7 days/week)'),
        ('extreme', 'Extremely Active (Intense exercise daily)'),
    ]
    
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintain', 'Maintain Current Weight'),
        ('improve_health', 'Improve Overall Health'),
        ('athlete', 'Athletic Performance'),
        ('manage_condition', 'Manage Health Condition'),
    ]
    
    CUISINE_PREFERENCES = [
        ('italian', 'Italian'),
        ('indian', 'Indian'),
        ('mexican', 'Mexican'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('thai', 'Thai'),
        ('mediterranean', 'Mediterranean'),
        ('middle_eastern', 'Middle Eastern'),
        ('american', 'American'),
        ('french', 'French'),
        ('korean', 'Korean'),
        ('spanish', 'Spanish'),
    ]
    
    COOKING_SKILL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Physical Information
    height_cm = models.FloatField(null=True, blank=True, validators=[MinValueValidator(100), MaxValueValidator(250)])
    weight_kg = models.FloatField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(300)])
    target_weight_kg = models.FloatField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(300)])
    
    # Health & Fitness
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, null=True, blank=True)
    daily_calorie_target = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(800), MaxValueValidator(5000)])
    
    # Dietary Preferences
    diet_type = models.CharField(max_length=50, null=True, blank=True)  # Vegetarian, Vegan, Keto, etc.
    preferred_cuisines = models.CharField(max_length=500, null=True, blank=True)  # JSON field would be better, but using CharField for simplicity
    cooking_skill = models.CharField(max_length=20, choices=COOKING_SKILL_CHOICES, default='intermediate')
    average_cooking_time = models.IntegerField(null=True, blank=True)  # In minutes
    kitchen_equipment = models.TextField(null=True, blank=True)  # Comma-separated
    
    # Allergies & Intolerances
    allergies = models.TextField(null=True, blank=True)  # Comma-separated: peanut, shellfish, etc.
    intolerances = models.TextField(null=True, blank=True)  # Comma-separated: dairy, gluten, etc.
    
    # Preferences
    favorite_ingredients = models.TextField(null=True, blank=True)  # Comma-separated
    disliked_ingredients = models.TextField(null=True, blank=True)  # Comma-separated
    budget_preference = models.CharField(
        max_length=20,
        choices=[
            ('economical', 'Economical'),
            ('moderate', 'Moderate'),
            ('premium', 'Premium'),
        ],
        default='moderate'
    )
    
    # Health Conditions (if any)
    diabetes = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    celiac = models.BooleanField(default=False)
    lactose_intolerant = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    other_conditions = models.TextField(null=True, blank=True)
    
    # Lifestyle
    meals_per_day = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    prefer_meal_prep = models.BooleanField(default=False)
    meal_prep_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly',
        null=True,
        blank=True
    )
    
    # Preferences for Recipe Recommendations
    min_recipe_rating = models.FloatField(default=3.5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    prefer_simple_recipes = models.BooleanField(default=True)
    prefer_healthy = models.BooleanField(default=True)
    spice_level = models.CharField(
        max_length=20,
        choices=[
            ('mild', 'Mild'),
            ('medium', 'Medium'),
            ('spicy', 'Spicy'),
            ('very_spicy', 'Very Spicy'),
        ],
        default='medium'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    preferences_completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def get_allergies_list(self):
        """Return allergies as a list"""
        if self.allergies:
            return [item.strip() for item in self.allergies.split(',')]
        return []
    
    def get_intolerances_list(self):
        """Return intolerances as a list"""
        if self.intolerances:
            return [item.strip() for item in self.intolerances.split(',')]
        return []
    
    def get_favorite_ingredients_list(self):
        """Return favorite ingredients as a list"""
        if self.favorite_ingredients:
            return [item.strip() for item in self.favorite_ingredients.split(',')]
        return []
    
    def get_disliked_ingredients_list(self):
        """Return disliked ingredients as a list"""
        if self.disliked_ingredients:
            return [item.strip() for item in self.disliked_ingredients.split(',')]
        return []
    
    def get_kitchen_equipment_list(self):
        """Return kitchen equipment as a list"""
        if self.kitchen_equipment:
            return [item.strip() for item in self.kitchen_equipment.split(',')]
        return []
