# Generated by Django 4.2.5 on 2023-10-29 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0006_ipaprediction_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ipaprediction',
            name='user',
        ),
        migrations.AddField(
            model_name='ipaprediction',
            name='submitted_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='predictions', to=settings.AUTH_USER_MODEL),
        ),
    ]