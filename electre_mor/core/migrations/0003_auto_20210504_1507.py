# Generated by Django 3.0.8 on 2021-05-04 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210504_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criterio',
            name='numerico',
            field=models.BooleanField(default=False),
        ),
    ]
