# Generated by Django 5.1.1 on 2024-09-24 18:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='item_name',
            new_name='item',
        ),
        migrations.RenameField(
            model_name='purchase',
            old_name='supplier_name',
            new_name='supplier',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='purchase_id',
        ),
        migrations.AddField(
            model_name='purchase',
            name='purchase_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]