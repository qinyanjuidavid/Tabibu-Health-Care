# Generated by Django 3.2.9 on 2022-05-26 06:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0009_auto_20220524_1233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medication',
            options={'verbose_name_plural': 'Prescription'},
        ),
        migrations.AlterModelOptions(
            name='medication_bag',
            options={'verbose_name_plural': 'Prescription Cart'},
        ),
        migrations.AddField(
            model_name='medication',
            name='date_dispenced',
            field=models.DateTimeField(null=True, verbose_name='date dispenced'),
        ),
        migrations.AlterField(
            model_name='appointments',
            name='appointment_time',
            field=models.TimeField(default=datetime.time(9, 30, 10, 941147), verbose_name='appointment time'),
        ),
    ]