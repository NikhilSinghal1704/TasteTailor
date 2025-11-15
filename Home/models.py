from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class APIKey(models.Model):
    key = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_called = models.DateTimeField(null=True, blank=True)
    call_history = models.JSONField(default=list)  # Store call counts for previous days

    def update_usage_count(self):
        now = timezone.now()
    
        # Check if the last_called time is before today (midnight)
        if not self.last_called or self.last_called.date() < now.date():
            # Reset usage count and update call history
            self.call_history.append({
                'date': str(self.last_called.date()) if self.last_called else str(now.date()),
                'count': self.usage_count
            })
            self.call_history = self.call_history[-10:]  # Limit to the last 10 days
            self.usage_count = 1
        else:
            self.usage_count += 1
    
        self.last_called = now
        self.save()


    def __str__(self):
        return self.key


class MealPlan(models.Model):
    """
    Stores a per-user daily meal plan (3 meals/day) generated from Spoonacular.
    """
    MEAL_TIMEFRAME_CHOICES = [
        ("day", "Day"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    date = models.DateField(help_text="Date for which this plan applies")
    timeframe = models.CharField(max_length=10, choices=MEAL_TIMEFRAME_CHOICES, default="day")

    # Aggregated daily nutrients returned by Spoonacular
    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)

    source_payload = models.JSONField(null=True, blank=True, help_text="Raw response snapshot for traceability")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "date", "timeframe")
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"MealPlan({self.user.username}, {self.date})"


class Meal(models.Model):
    """
    Individual meal entries belonging to a MealPlan.
    """
    MEAL_TYPE_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
    ]

    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="meals")

    # Spoonacular recipe basics
    spoonacular_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)

    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    ready_in_minutes = models.PositiveIntegerField(null=True, blank=True)
    servings = models.PositiveIntegerField(null=True, blank=True)

    # Optional per-meal nutrition (if later enriched)
    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)

    extra = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.meal_type})"


class GeneratedRecipe(models.Model):
    """Stores AI-generated recipes per user with structured payload."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="generated_recipes")
    prompt = models.TextField(help_text="User request that triggered generation")
    title = models.CharField(max_length=255)
    data = models.JSONField(help_text="Structured recipe content produced by AI")

    # Snapshot of applied constraints
    diet_type = models.CharField(max_length=50, null=True, blank=True)
    vegetarian = models.BooleanField(default=False)
    vegan = models.BooleanField(default=False)
    excluded_ingredients = models.TextField(null=True, blank=True, help_text="Comma-separated excluded ingredients/allergens")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class PantryItem(models.Model):
    """User pantry ingredient entries to power ingredient-based search."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pantry_items")
    name = models.CharField(max_length=120)
    spoonacular_id = models.PositiveIntegerField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    aisle = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.user.username})"
