# Generated by Django 3.2.9 on 2022-05-29 06:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_alter_appointments_appointment_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='appointment_time',
            field=models.TimeField(default=datetime.time(9, 32, 3, 363519), verbose_name='appointment time'),
        ),
        migrations.AlterField(
            model_name='appointments',
            name='status',
            field=models.CharField(choices=[('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('In Progress', 'In Progress'), ('Pending', 'Pending')], default='Pending', max_length=20, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='test',
            name='date_tested',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date tested'),
        ),
    ]
