# Generated by Django 3.2 on 2023-09-26 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_title_rating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
