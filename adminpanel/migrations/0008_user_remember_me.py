# Generated by Django 3.1.4 on 2020-12-28 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0007_user_is_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='remember_me',
            field=models.BooleanField(default=False),
        ),
    ]
