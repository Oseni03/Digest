# Generated by Django 5.0 on 2024-01-30 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('niche', '0004_niche_description_niche_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='niche',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
