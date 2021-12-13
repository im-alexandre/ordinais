import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django_pandas.managers import DataFrameManager


class Decisor(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nome', 'projeto'],
                                    name='unique_decisor')
        ]

    projeto = models.ForeignKey('Projeto',
                                related_name='decisores',
                                on_delete=models.CASCADE,
                                null=True)
    nome = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    nome = models.CharField(max_length=20)
    descricao = models.TextField(max_length=400)
    qtde_classes = models.IntegerField(null=False,
                                       validators=[MinValueValidator(2)])
    qtde_criterios = models.IntegerField(null=False,
                                         validators=[MinValueValidator(2)])
    qtde_alternativas = models.IntegerField(null=False,
                                            validators=[MinValueValidator(2)])
    qtde_decisores = models.IntegerField(null=False,
                                         validators=[MinValueValidator(1)])
    lamb = models.FloatField(
        null=False,
        blank=False,
        default=0.5,
        validators=[MinValueValidator(0.5),
                    MaxValueValidator(1)])

    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    def delete_old(self):
        two_days_ago = timezone.now() - datetime.timedelta(days=7)
        self.filter(data__lt=two_days_ago).delete()


class Alternativa(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nome', 'projeto'],
                                    name='unique_alternativa')
        ]

    projeto = models.ForeignKey('Projeto',
                                on_delete=models.CASCADE,
                                related_name='alternativas',
                                null=True)
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Criterio(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nome', 'projeto'],
                                    name='unique_criterio')
        ]

    escolhas = ((1, "increasing"), (2, "decreasing"))
    projeto = models.ForeignKey('Projeto',
                                related_name='criterios',
                                on_delete=models.CASCADE,
                                null=True)
    nome = models.CharField(max_length=20, blank=False, null=False)
    numerico = models.BooleanField()
    monotonico = models.IntegerField(choices=escolhas, default=1)

    def __str__(self):
        return self.nome


class AvaliacaoCriterios(models.Model):
    projeto = models.ForeignKey('Projeto',
                                on_delete=models.CASCADE,
                                related_name='avaliacaocriterios')
    decisor = models.ForeignKey('Decisor',
                                on_delete=models.CASCADE,
                                related_name='avaliacaocriterios')
    criterioA = models.ForeignKey('Criterio',
                                  on_delete=models.CASCADE,
                                  related_name='criterioA')
    criterioB = models.ForeignKey('Criterio',
                                  on_delete=models.CASCADE,
                                  related_name='criterioB')
    nota = models.IntegerField(null=False, default=0)
    objects = DataFrameManager()


class AvaliacaoAlternativas(models.Model):
    projeto = models.ForeignKey('Projeto',
                                on_delete=models.CASCADE,
                                related_name='avaliacaoalternativas')
    decisor = models.ForeignKey('Decisor',
                                on_delete=models.CASCADE,
                                related_name='avaliacaoalternativas')
    criterio = models.ForeignKey('Criterio',
                                 on_delete=models.CASCADE,
                                 related_name='avaliacaoalternativas')
    alternativaA = models.ForeignKey('Alternativa',
                                     on_delete=models.CASCADE,
                                     related_name='alternativaA')
    alternativaB = models.ForeignKey('Alternativa',
                                     on_delete=models.CASCADE,
                                     related_name='alternativaB')
    nota = models.IntegerField(null=True)

    objects = DataFrameManager()


class AlternativaCriterio(models.Model):
    projeto = models.ForeignKey('Projeto',
                                on_delete=models.CASCADE,
                                related_name='alternativacriterios')
    criterio = models.ForeignKey('Criterio',
                                 on_delete=models.CASCADE,
                                 related_name='alternativacriterio')
    alternativa = models.ForeignKey('Alternativa',
                                    on_delete=models.CASCADE,
                                    related_name='alternativacriterio')

    nota = models.FloatField(null=True)

    objects = DataFrameManager()


class CriterioParametro(models.Model):
    projeto = models.ForeignKey('Projeto',
                                on_delete=models.CASCADE,
                                related_name='criterioparametro')
    criterio = models.ForeignKey('Criterio',
                                 on_delete=models.CASCADE,
                                 related_name='criterioparametro')
    p = models.FloatField()
    q = models.FloatField()
    v = models.FloatField()

    objects = DataFrameManager()
