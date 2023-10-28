from django.db import migrations
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

def create_admins_with_tokens(apps, schema_editor):
    # Define a list of admins with usernames and passwords
    admins = [
        {'username': 'admin1', 'password': 'password123'},
        {'username': 'admin2', 'password': 'password234'},
        {'username': 'admin3', 'password': 'password345'}
    ]

    for admin in admins:
        user = User.objects.create_superuser(username=admin['username'], password=admin['password'], email='')

        # Assuming the Admin group already exists, but creating it just in case it doesn't
        admin_group, created = Group.objects.get_or_create(name='Admin')
        admin_group.user_set.add(user)

        # Create a token for the admin user
        Token.objects.create(user=user)

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_ipaprediction_submission_date'),
    ]

    operations = [
        migrations.RunPython(create_admins_with_tokens),
    ]
