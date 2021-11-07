from django.core.validators import MinValueValidator
from django.db import models
from django_pandas.managers import DataFrameManager

# Create your models here.


class Projeto(models.Model):
    """Classe para salvar o projeto """
    nome = models.CharField(max_length=20, null=False, blank=False)
    num_alternativas = models.IntegerField(validators=[MinValueValidator(2)])
    num_criterios = models.IntegerField(validators=[MinValueValidator(2)])


class Alternativa(models.Model):
    nome = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome


class Criterio(models.Model):
    escolhas = ((1, "Increasing"), (2, "Decreasing"))
    nome = models.CharField(max_length=20, blank=False, null=False)
    monotonico = models.IntegerField(choices=escolhas, null=False, blank=False)

    def __str__(self):
        return self.nome


class AlternativaCriterio(models.Model):
    criterio = models.ForeignKey('Criterio',
                                 on_delete=models.CASCADE,
                                 related_name='criterio',
                                 null=False,
                                 blank=False)
    alternativa = models.ForeignKey('Alternativa',
                                    on_delete=models.CASCADE,
                                    related_name='alternativa',
                                    null=False,
                                    blank=False)
    nota = models.FloatField(null=False, blank=False)
    objects = DataFrameManager()
