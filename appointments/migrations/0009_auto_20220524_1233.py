# Generated by Django 3.2.9 on 2022-05-24 09:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20220521_1646'),
        ('appointments', '0008_auto_20220524_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='appointment_time',
            field=models.TimeField(default=datetime.time(12, 33, 44, 148755), verbose_name='appointment time'),
        ),
        migrations.AlterField(
            model_name='medication',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.doctor'),
        ),
        migrations.AlterField(
            model_name='test',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.doctor'),
        ),
    ]