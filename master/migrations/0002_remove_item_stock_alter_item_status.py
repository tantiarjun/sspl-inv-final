# Generated by Django 5.1.1 on 2024-09-21 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='stock',
        ),
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]