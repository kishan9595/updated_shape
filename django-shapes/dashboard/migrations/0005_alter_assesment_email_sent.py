# Generated by Django 4.0.2 on 2022-03-03 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_clienttable_theropy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assesment',
            name='email_sent',
            field=models.CharField(default='', max_length=10),
        ),
    ]
