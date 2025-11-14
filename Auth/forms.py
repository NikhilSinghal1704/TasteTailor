from django import forms
from .models import UserPreferences

class PreferencesForm(forms.ModelForm):
    """Form for user preferences"""
    
    # Additional fields for better form handling
    allergies = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Peanuts, Shellfish, Dairy (comma-separated)',
            'data-role': 'tagsinput'
        }),
        help_text='Enter allergies separated by commas'
    )
    
    intolerances = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Gluten, Lactose (comma-separated)',
            'data-role': 'tagsinput'
        }),
        help_text='Enter intolerances separated by commas'
    )
    
    favorite_ingredients = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Chicken, Broccoli, Olive Oil (comma-separated)',
            'data-role': 'tagsinput'
        }),
        help_text='Enter your favorite ingredients separated by commas'
    )
    
    disliked_ingredients = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Mushrooms, Cilantro (comma-separated)',
            'data-role': 'tagsinput'
        }),
        help_text='Enter ingredients you dislike separated by commas'
    )
    
    kitchen_equipment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Oven, Blender, Rice Cooker (comma-separated)',
            'data-role': 'tagsinput'
        }),
        help_text='Enter available kitchen equipment separated by commas'
    )
    
    class Meta:
        model = UserPreferences
        fields = [
            'first_name', 'last_name', 'date_of_birth',
            'height_cm', 'weight_kg', 'target_weight_kg',
            'goal', 'activity_level', 'daily_calorie_target',
            'diet_type', 'cooking_skill', 'average_cooking_time',
            'allergies', 'intolerances', 'favorite_ingredients',
            'disliked_ingredients', 'budget_preference',
            'diabetes', 'hypertension', 'celiac', 'lactose_intolerant',
            'heart_disease', 'other_conditions', 'meals_per_day',
            'prefer_meal_prep', 'meal_prep_frequency', 'spice_level',
            'kitchen_equipment', 'bio'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'required': True
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself (optional)',
                'maxlength': 500
            }),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm (e.g., 175)',
                'step': 0.5,
                'min': 100,
                'max': 250
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Current weight in kg (e.g., 75)',
                'step': 0.5,
                'min': 30,
                'max': 300
            }),
            'target_weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target weight in kg (optional)',
                'step': 0.5,
                'min': 30,
                'max': 300
            }),
            'goal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'daily_calorie_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2000',
                'min': 800,
                'max': 5000
            }),
            'diet_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Vegetarian, Vegan, Keto'
            }),
            'cooking_skill': forms.Select(attrs={
                'class': 'form-select'
            }),
            'average_cooking_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Average cooking time in minutes',
                'min': 5,
                'max': 180
            }),
            'budget_preference': forms.Select(attrs={
                'class': 'form-select'
            }),
            'meals_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 6,
                'type': 'number'
            }),
            'prefer_meal_prep': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meal_prep_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'spice_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'other_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe any other health conditions'
            }),
            'diabetes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hypertension': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'celiac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'lactose_intolerant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'heart_disease': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
