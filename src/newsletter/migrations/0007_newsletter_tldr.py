# Generated by Django 5.0 on 2024-01-31 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0006_subscription_is_active_alter_subscription_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='tldr',
            field=models.TextField(default='Lorem ipsum dolor sit amet, consectetur adipisicing elit. Assumenda.'),
            preserve_default=False,
        ),
    ]
