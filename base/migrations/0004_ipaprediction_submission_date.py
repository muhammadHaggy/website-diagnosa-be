# Generated by Django 4.2.5 on 2023-10-27 11:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_ipaprediction_is_high_risk'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipaprediction',
            name='submission_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]