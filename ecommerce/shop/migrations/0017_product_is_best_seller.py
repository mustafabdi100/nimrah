# Generated by Django 5.1.1 on 2024-09-16 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_product_is_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_best_seller',
            field=models.BooleanField(default=False),
        ),
    ]
