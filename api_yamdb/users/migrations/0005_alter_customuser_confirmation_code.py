# Generated by Django 3.2 on 2023-09-27 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230926_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='confirmation_code',
            field=models.TextField(default='BHydzpamSvLc'),
        ),
    ]
