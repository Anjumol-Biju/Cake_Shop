# Generated by Django 5.0.1 on 2024-03-26 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cakeshop', '0007_alter_basket_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='basketitem',
            old_name='occation_object',
            new_name='occasion_object',
        ),
    ]
