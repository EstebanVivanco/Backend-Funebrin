# Generated by Django 5.0.6 on 2024-11-10 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0004_product_capacity_product_color_product_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]