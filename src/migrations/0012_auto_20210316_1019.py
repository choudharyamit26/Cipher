# Generated by Django 3.1.2 on 2021-03-16 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0011_readmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='mode',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(default='', max_length=256)),
                ('coins', models.IntegerField(default=0)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=3)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='src.appuser')),
            ],
        ),
    ]
