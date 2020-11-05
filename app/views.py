from datetime import datetime
from itertools import product

import pandas as pd

from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import AlternativaCriterioForm, AlternativaForm, CriterioForm
from .metodos import condorcet
from .metodos.borda_cardinal import borda
from .models import Alternativa, AlternativaCriterio, Criterio


def index(request):
    """docstring"""
    return render(request, 'index.html')


def form(request):
    """docstring for form"""
    criteriosformset = modelformset_factory(model=Criterio,
                                            fields=('nome', 'monotonico'),
                                            min_num=2,
                                            extra=0)
    alternativasformset = modelformset_factory(model=Alternativa,
                                               fields=('nome', ),
                                               min_num=2,
                                               extra=0)

    criterios_form_set = criteriosformset(queryset=Criterio.objects.none(),
                                          prefix="critform")
    alternativas_form_set = alternativasformset(
        queryset=Alternativa.objects.none(), prefix="altform")
    return render(
        request, 'cadastra_criterios_alternativas.html', {
            'criterio_form_set': criterios_form_set,
            'alternativa_form_set': alternativas_form_set
        })


def salva_criterios_alternativas(request):
    """docstring for salva_criterios_alternativas"""
    if request.method == 'POST':
        criteriosformset = modelformset_factory(model=Criterio,
                                                fields=('nome', 'monotonico'),
                                                min_num=2,
                                                extra=0)
        alternativasformset = modelformset_factory(model=Alternativa,
                                                   fields=('nome', ),
                                                   min_num=2,
                                                   extra=0)

        criterios = criteriosformset(request.POST, prefix='critform').save()
        alternativas = alternativasformset(request.POST,
                                           prefix='altform').save()
        request.session['criterios'] = [criterio.id for criterio in criterios]
        request.session['alternativas'] = [
            alternativa.id for alternativa in alternativas
        ]

    return redirect('avalia')


def avalia(request):
    """docstring for resultado"""
    criterios = request.session['criterios']
    lista_criterios = list(Criterio.objects.filter(id__in=criterios))
    alternativas = request.session['alternativas']
    lista_alternativas = list(Alternativa.objects.filter(id__in=alternativas))
    combinacoes = list(product(lista_criterios, lista_alternativas))
    avalia_formset = formset_factory(form=AlternativaCriterioForm, extra=0)
    formset = avalia_formset(initial=[{
        'alternativa': alternativa,
        'criterio': criterio
    } for criterio, alternativa in combinacoes])

    return render(request, 'avalia.html', {
        'avalia_formset': formset,
    })


def resultado(request):
    if request.method == 'POST':
        criterios = request.session['criterios']
        lista_criterios = list(Criterio.objects.filter(id__in=criterios))
        alternativas = request.session['alternativas']
        lista_alternativas = list(
            Alternativa.objects.filter(id__in=alternativas))
        avalia_formset = formset_factory(form=AlternativaCriterioForm)
        avaliacoes = avalia_formset(request.POST)
        notas = list()
        if avaliacoes.is_valid():
            for avaliacao in avaliacoes:
                nota = avaliacao.save()
                notas.append(nota.id)

        df = AlternativaCriterio.objects.filter(id__in=notas)
        df = df.to_dataframe().drop(columns=['id'])
        df = df.pivot_table(values='nota',
                            index='alternativa',
                            columns='criterio')
        for criterio in lista_criterios:
            print(criterio.monotonico)
            if criterio.monotonico == 2:
                df[criterio.nome] = df[criterio.nome].apply(lambda x: x * -1)
        df_condorcet = condorcet.condorcet(df)
        df_borda = borda(df)

    return render(
        request, 'resultado.html', {
            'df_borda': df_borda.to_html(),
            'df_condorcet': df_condorcet['condorcet'].to_html(),
            'df_copeland': df_condorcet['copeland'].to_html()
        })
