# Generated by Django 3.2 on 2023-09-30 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_customuser_confirmation_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='confirmation_code',
            field=models.TextField(default='XeAiKJOjfCnF'),
        ),
    ]
