from django.db import models
from django.utils import timezone


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
