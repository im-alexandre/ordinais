# Generated by Django 3.1.3 on 2021-05-02 19:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alternativa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Criterio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
                ('monotonico', models.IntegerField(choices=[(1, 'Increasing'), (2, 'Decreasing')])),
            ],
        ),
        migrations.CreateModel(
            name='Projeto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
                ('num_alternativas', models.IntegerField(validators=[django.core.validators.MinValueValidator(2)])),
                ('num_criterios', models.IntegerField(validators=[django.core.validators.MinValueValidator(2)])),
            ],
        ),
        migrations.CreateModel(
            name='AlternativaCriterio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.FloatField()),
                ('alternativa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alternativa', to='app.alternativa')),
                ('criterio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='criterio', to='app.criterio')),
            ],
        ),
    ]
