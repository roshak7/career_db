# Generated by Django 2.2.24 on 2024-02-26 14:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('career', '0022_persons_position_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='person_profile',
            name='jdata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='JSON данные'),
        ),
    ]
