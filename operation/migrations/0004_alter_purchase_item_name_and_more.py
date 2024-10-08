# Generated by Django 5.1.1 on 2024-09-25 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0006_supplier_created_at'),
        ('operation', '0003_rename_name_item_item_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='item_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.item'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='supplier_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.supplier'),
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='purchase_date',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
    ]
