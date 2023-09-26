# Generated by Django 3.2 on 2023-09-26 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20230926_1526'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('author', 'title'), name='unique_author_title'),
        ),
    ]