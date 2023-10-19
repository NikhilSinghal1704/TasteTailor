from django.db import models

class APIKey(models.Model):
    key = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)  # Add an email field to associate with the key
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.key
