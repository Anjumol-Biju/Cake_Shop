# Generated by Django 5.0.1 on 2024-03-25 09:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakeshop', '0003_basketitem_is_order_placed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='basketitem',
            name='flavour_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cakeshop.flavour'),
        ),
    ]
