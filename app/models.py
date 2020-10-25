from django.db import models
from django_pandas.managers import DataFrameManager
# Create your models here.


class Alternativa(models.Model):
    nome = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome


class Criterio(models.Model):
    escolhas = ((1, "lucro"), (2, "custo"))
    nome = models.CharField(max_length=20, blank=False, null=False)
    monotonico = models.IntegerField(choices=escolhas, null=False, blank=False)

    def __str__(self):
        return self.nome


class AlternativaCriterio(models.Model):
    criterio = models.ForeignKey('Criterio',
                                 on_delete=models.CASCADE,
                                 related_name='criterio')
    alternativa = models.ForeignKey('Alternativa',
                                    on_delete=models.CASCADE,
                                    related_name='alternativa')
    nota = models.FloatField(null=True)
    objects = DataFrameManager()
