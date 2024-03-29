# Generated by Django 4.2.6 on 2023-10-19 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0003_remove_apikey_rotation_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='call_history',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='apikey',
            name='last_called',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='apikey',
            name='usage_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
