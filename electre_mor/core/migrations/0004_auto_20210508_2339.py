# Generated by Django 3.0.8 on 2021-05-09 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210504_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criterio',
            name='numerico',
            field=models.BooleanField(),
        ),
    ]
