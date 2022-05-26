# Generated by Django 3.2.9 on 2022-05-23 16:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0006_alter_appointments_appointment_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='appointment_time',
            field=models.TimeField(default=datetime.time(19, 39, 10, 502573), verbose_name='appointment time'),
        ),
        migrations.AlterField(
            model_name='test',
            name='results',
            field=models.TextField(blank=True, null=True, verbose_name='results'),
        ),
    ]