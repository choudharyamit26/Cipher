# Generated by Django 3.1.4 on 2021-02-02 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0007_auto_20210122_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='profile_pic',
            field=models.ImageField(blank=True, default='default_profile.png', null=True, upload_to=''),
        ),
    ]
