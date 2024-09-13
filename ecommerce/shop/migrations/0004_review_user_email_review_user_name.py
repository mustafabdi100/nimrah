# Generated by Django 5.1.1 on 2024-09-07 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='user_email',
            field=models.EmailField(default='example@example.com', max_length=254),
        ),
        migrations.AddField(
            model_name='review',
            name='user_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
