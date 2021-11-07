import mimetypes
import os
from datetime import datetime
from itertools import product

import pandas as pd

from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import (AlternativaCriterioForm, AlternativaForm, CriterioForm,
                    ProjetoForm)
from .metodos.condorcet_copeland import condorcet_copeland
from .metodos.borda import borda
from .models import Alternativa, AlternativaCriterio, Criterio


def index(request):
    """docstring"""
    return render(request, 'index.html')


def projeto_form(request):
    """view para definir o número de alternativas e critérios"""
    formulario = ProjetoForm()

    return render(request, 'projeto_form.html', context={'form': formulario})


def salva_projeto(request):
    """validar os parâmetros do projeto"""
    if request.method == 'POST':
        formulario_projeto = ProjetoForm(request.POST)
        if formulario_projeto.is_valid():
            info_projeto = formulario_projeto.save()
            request.session['id_projeto'] = info_projeto.id
            request.session[
                'qtde_alternativas'] = info_projeto.num_alternativas
            request.session['qtde_criterios'] = info_projeto.num_criterios
            request.session['nome_projeto'] = info_projeto.nome
            return redirect('form')
    return redirect('projeto_form')


def form(request):
    """docstring for form"""
    criteriosformset = modelformset_factory(
        model=Criterio,
        fields=('nome', 'monotonico'),
        min_num=request.session['qtde_criterios'],
        extra=0)
    alternativasformset = modelformset_factory(
        model=Alternativa,
        fields=('nome', ),
        min_num=request.session['qtde_alternativas'],
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

        criterios = criteriosformset(request.POST, prefix='critform')
        alternativas = alternativasformset(request.POST, prefix='altform')
        if criterios.is_valid() and alternativas.is_valid():
            criterios = criterios.save()
            alternativas = alternativas.save()
            request.session['criterios'] = [
                criterio.id for criterio in criterios
            ]
            request.session['alternativas'] = [
                alternativa.id for alternativa in alternativas
            ]

            return redirect('avalia')
    return redirect('form')


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
        avalia_formset = formset_factory(form=AlternativaCriterioForm)
        avaliacoes = avalia_formset(request.POST)
        notas = list()
        if avaliacoes.is_valid():
            for avaliacao in avaliacoes:
                nota = avaliacao.save()
                notas.append(nota.id)
        else:
            return redirect('avalia')

        saida = pd.ExcelWriter(str(request.session['id_projeto']) + '.xlsx')
        df = AlternativaCriterio.objects.filter(id__in=notas)
        df = df.to_dataframe().drop(columns=['id'])
        df = df.pivot_table(values='nota',
                            index='alternativa',
                            columns='criterio')
        for criterio in lista_criterios:
            if criterio.monotonico == 2:
                df[criterio.nome] = df[criterio.nome].apply(lambda x: x * -1)
        df_condorcet = condorcet_copeland(df, request.session['id_projeto'],
                                           saida)
        df_borda = borda(df)
        df_borda.to_excel(saida, sheet_name='borda')
        saida.save()

    return render(
        request, 'resultado.html', {
            'df_borda':
            df_borda[['Score', 'Rank']].to_html(),
            'df_condorcet':
            df_condorcet['condorcet'][['Score', 'Rank']].to_html(),
            'df_copeland':
            df_condorcet['copeland'][['Score', 'Rank']].to_html()
        })


def relatorio(request):
    """docstring for relatório"""
    fl_path = str(request.session['id_projeto']) + '.xlsx'
    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % fl_path
    os.remove(fl_path)
    # Alternativa.objects.filter(id__in=request.session['alternativas']).delete()
    return response
