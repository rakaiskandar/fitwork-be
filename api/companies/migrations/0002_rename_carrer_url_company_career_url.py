# Generated by Django 4.2.21 on 2025-05-13 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='carrer_url',
            new_name='career_url',
        ),
    ]
