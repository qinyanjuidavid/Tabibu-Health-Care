# Generated by Django 3.2.9 on 2022-05-21 13:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_auto_20220520_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='appointment_time',
            field=models.TimeField(default=datetime.time(16, 46, 6, 148281), verbose_name='appointment time'),
        ),
    ]
