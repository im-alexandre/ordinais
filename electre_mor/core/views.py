import mimetypes
import warnings
import zipfile
from itertools import combinations, product

import pandas as pd
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _

from core.forms import (AlternativaCriterioForm, AvaliacaoAlternativasForm,
                        AvaliacaoCriteriosForm, CriterioParametroForm,
                        NomeProjetoForm)
from core.models import (Alternativa, AlternativaCriterio,
                         AvaliacaoAlternativas, AvaliacaoCriterios, Criterio,
                         CriterioParametro, Decisor, Projeto)

from .ElectreTri import ElectreTri
from .method import MatrizProjeto

warnings.filterwarnings('ignore')
pd.options.display.float_format = '{:,.4f}'.format


def landing_page(request):
    """docstring"""
    return render(request, 'landing_page.html')


def index(request):
    template_name = 'index.html'
    projetos = Projeto.objects.all()

    if request.method == "POST":
        nome_projeto_form = NomeProjetoForm(request.POST)
        if nome_projeto_form.is_valid():
            projeto_novo = nome_projeto_form.save()
            return redirect('cadastradecisores', projeto_id=projeto_novo.id)
        else:
            return render(request, template_name, {
                'form': nome_projeto_form,
                'projetos': projetos,
            })

    else:
        nome_projeto_form = NomeProjetoForm()

        return render(request, template_name, {
            'form': nome_projeto_form,
            'projetos': projetos,
        })


def metodo(request):
    template_name = 'metodo.html'

    return render(request, template_name)


def projeto(request, projeto_id):
    template_name = 'projeto.html'
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = Decisor.objects.filter(projeto=projeto_id)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id)

    return render(
        request, template_name, {
            'projeto': projeto,
            'decisores': decisores,
            'alternativas': alternativas,
            'criterios': criterios
        })


def deletarprojeto(request, projeto_id):
    redirect_page = '/'
    params_redirect = ''

    try:
        projeto = Projeto.objects.get(id=projeto_id)
        projeto.delete()
    except:
        redirect_page = 'resultado'
        params_redirect = projeto_id

    return redirect(redirect_page, projeto_id=params_redirect)


def cadastradecisores(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_decisores.html'
    decisores = projeto.decisores.all()
    criterios = projeto.criterios.all()
    alternativas = projeto.criterios.all()
    decisores_nome = {decisor.nome for decisor in decisores}
    criterios_nome = {criterio.nome for criterio in criterios}
    alternativas_nome = {alternativa.nome for alternativa in alternativas}

    decisoresformset = modelformset_factory(model=Decisor,
                                            fields=('nome', ),
                                            extra=projeto.qtde_decisores -
                                            projeto.decisores.count(),
                                            labels={'nome': 'Name'})

    criteriosformset = modelformset_factory(
        model=Criterio,
        fields=('nome', 'numerico', 'monotonico'),
        extra=projeto.qtde_criterios - projeto.criterios.count(),
        labels={
            'numerico': _("Criterion's type: "),
            'nome': 'Name: ',
            'monotonico': 'Monotonicity: '
        },
        widgets={
            'numerico':
            forms.Select(choices=((True, "Numeric"), (False, "Qualitative")),
                         attrs={
                             'onchange': 'esconde_monotonico(this)',
                             'class': 'check'
            }),
            'monotonico':
            forms.Select(choices=((1, "Benefit"), (2, "Cost")),
                         attrs={'class': 'monotonico'})
        })
    alternativasformset = modelformset_factory(
        model=Alternativa,
        fields=('nome', ),
        extra=projeto.qtde_alternativas - projeto.criterios.count(),
        labels={'nome': 'Name: '})

    criterio_form_set = criteriosformset(
        queryset=criterios,
        prefix='critform',
    )
    decisor_form_set = decisoresformset(
        queryset=decisores,
        prefix='decform',
    )
    alternativa_form_set = alternativasformset(
        queryset=alternativas,
        prefix='altform',
    )

    if request.method == 'POST':
        decisor_form_set, criterios_form_set, alternativa_form_set = (
            decisoresformset(request.POST, prefix='decform'),
            criteriosformset(request.POST, prefix='critform'),
            alternativasformset(request.POST, prefix='altform'))

        if all([
                decisor_form_set.is_valid(),
                alternativa_form_set.is_valid(),
                criterios_form_set.is_valid()
        ]):
            for decisor_form in decisor_form_set:
                if decisor_form.is_valid():
                    decisor_novo = decisor_form.save()
                    decisor_novo.projeto = projeto
                    decisor_novo.save()

            for alternativa_form in alternativa_form_set:
                if alternativa_form.is_valid():
                    nova_alternativa = alternativa_form.save()
                    nova_alternativa.projeto = projeto
                    nova_alternativa.save()

            for criterio_form in criterios_form_set:
                if criterio_form.is_valid():
                    criterio_novo = criterio_form.save()
                    criterio_novo.projeto = projeto
                    criterio_novo.save()

            return redirect('alternativacriterio', projeto_id=projeto.id)
    return render(
        request, template_name, {
            'decisor_form_set': decisor_form_set,
            'criterio_form_set': criterio_form_set,
            'alternativa_form_set': alternativa_form_set,
            'projeto': projeto,
        })


def alternativacriterio(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'alternativacriterio.html'
    alternativas = list(Alternativa.objects.filter(projeto=projeto))
    criterios = list(Criterio.objects.filter(projeto=projeto, numerico=True))
    combinacoes = list(product(alternativas, criterios))
    alternativa_criterio_queryset = list(
        AlternativaCriterio.objects.filter(projeto=projeto))
    formset = formset_factory(form=AlternativaCriterioForm, extra=0)
    if len(criterios) == 0:
        return redirect('avaliarcriterios', projeto_id=projeto_id)
    if request.method == 'GET':
        if alternativa_criterio_queryset:
            forms = formset(initial=[{
                'projeto': i.projeto,
                'criterio': i.criterio,
                'alternativa': i.alternativa,
                'nota': i.nota
            } for i in alternativa_criterio_queryset])
        else:
            forms = formset(initial=[{
                'projeto': projeto,
                'criterio': criterio,
                'alternativa': alternativa
            } for (alternativa, criterio) in combinacoes])
        return render(request, template_name, {
            'forms': forms,
            'projeto': projeto,
        })

    if request.method == 'POST':
        alternativa_criterio_formset = formset(request.POST)
        if alternativa_criterio_formset.is_valid():
            AlternativaCriterio.objects.filter(projeto=projeto).delete()
            for altcritform in alternativa_criterio_formset:
                if altcritform.is_valid():
                    altcrit = altcritform.save()
                    altcrit.projeto = projeto
                    altcrit.save()
        return redirect('avaliarcriterios', projeto_id=projeto.id)


def avaliarcriterios(request, projeto_id):
    '''
    View para avaliar os critérios cadastrados.
    '''
    template_name = 'avaliar_criterios.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = Decisor.objects.filter(projeto=projeto_id)
    criterios = list(Criterio.objects.filter(projeto=projeto_id))
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    avaliacao_criterios_queryset = list(
        AvaliacaoCriterios.objects.filter(projeto=projeto))

    criterios_combinados = list(combinations(criterios, 2))

    formset = formset_factory(form=AvaliacaoCriteriosForm, extra=0)

    if request.method == 'GET':
        if avaliacao_criterios_queryset:
            forms = formset(initial=[{
                'projeto': i.projeto,
                'decisor': i.decisor,
                'criterioA': i.criterioA,
                'criterioB': i.criterioB,
                'nota': i.nota
            } for i in avaliacao_criterios_queryset])
        else:
            forms = formset(initial=[{
                'projeto': projeto,
                'decisor': decisor,
                'criterioA': criterio,
                'criterioB': alternativa
            } for decisor, (
                alternativa,
                criterio) in product(decisores, criterios_combinados)])

    if request.method == 'POST':
        avaliacao_criterios_formset = formset(request.POST)
        if avaliacao_criterios_formset.is_valid():
            AvaliacaoCriterios.objects.filter(projeto=projeto).delete()
            for aval_crit in avaliacao_criterios_formset:
                if aval_crit.is_valid():
                    avalcrit = aval_crit.save()
                    avalcrit.nota = int(avalcrit.nota)
                    avalcrit.save()
                    avalcrit.pk = None
                    avalcrit.criterioA, avalcrit.criterioB = avalcrit.criterioB, avalcrit.criterioA
                    avalcrit.nota = -avalcrit.nota
                    avalcrit.save()

        if len(alternativas) > 1:
            return redirect('avaliaralternativas', projeto_id)
        else:
            return redirect('resultado', projeto_id)

    return render(
        request, template_name, {
            'campos': request,
            'decisores': decisores,
            'forms': forms,
            'projeto': projeto,
        })


def avaliaralternativas(request, projeto_id):
    '''
    View para avaliar as alternativas cadastradas.
    '''
    projeto = Projeto.objects.get(id=projeto_id)
    if not projeto.criterios.filter(numerico=False):
        return redirect('resultadosapevo', projeto_id)
    template_name = 'avaliar_alternativas.html'
    projeto_id = projeto_id
    decisores = projeto.decisores.all()
    criterios = projeto.criterios.filter(numerico=False)
    alternativas = projeto.alternativas.all()
    avaliacoes_alternativas_queryset = list(
        AvaliacaoAlternativas.objects.filter(projeto=projeto))

    alternativas_combinadas = list(combinations(alternativas, 2))

    formset = formset_factory(form=AvaliacaoAlternativasForm, extra=0)

    if request.method == 'GET':
        if avaliacoes_alternativas_queryset:
            forms = formset(initial=[{
                'projeto': i.projeto,
                'decisor': i.decisor,
                'criterio': i.criterio,
                'alternativaA': i.alternativaA,
                'alternativaB': i.alternativaB,
                'nota': i.nota
            } for i in avaliacoes_alternativas_queryset])
        else:
            forms = formset(initial=[{
                'projeto': projeto,
                'decisor': decisor,
                'criterio': criterio,
                'alternativaA': alternativaA,
                'alternativaB': alternativaB,
            } for decisor, criterio, (alternativaA, alternativaB) in product(
                decisores, criterios, alternativas_combinadas)])

    if request.method == 'POST':
        avaliacao_criterios_formset = formset(request.POST)
        if avaliacao_criterios_formset.is_valid():
            AvaliacaoAlternativas.objects.filter(projeto=projeto).delete()
            for aval_crit in avaliacao_criterios_formset:
                if aval_crit.is_valid():
                    avalcrit = aval_crit.save()
                    avalcrit.projeto = projeto
                    avalcrit.nota = int(avalcrit.nota)
                    avalcrit.save()
                    avalcrit.pk = None
                    avalcrit.alternativaA, avalcrit.alternativaB = avalcrit.alternativaB, avalcrit.alternativaA
                    avalcrit.nota = -avalcrit.nota
                    avalcrit.save()

        return redirect('resultadosapevo', projeto_id)

    return render(
        request, template_name, {
            'decisores': decisores,
            'forms': forms,
            'criterios': criterios,
            'projeto': projeto,
        })


def resultado_sapevo(request, projeto_id):
    """docstring for resultado_sapevo"""
    projeto = Projeto.objects.get(id=projeto_id)
    matriz = MatrizProjeto(projeto)
    criterios = list(Criterio.objects.filter(projeto=projeto_id))
    pesos = matriz.pesos_criterios
    pesos.sort_values(by='peso', ascending=False, inplace=True)
    pesos = pesos.to_html(index=False)
    valores = AlternativaCriterio.objects.filter(projeto=projeto)
    valores = valores.to_dataframe().to_html()
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    criterios_quali = list(projeto.criterios.filter(numerico=False))
    df_criterios = matriz.avaliacoes['criterios'].to_html()
    formsetQuali = formset_factory(form=CriterioParametroForm, extra=0)
    criterio_parametro_queryset = list(
        CriterioParametro.objects.filter(projeto=projeto))

    if request.method == 'GET':
        if criterio_parametro_queryset:
            formsQuali = formsetQuali(initial=[{
                'projeto': i.projeto,
                'criterio': i.criterio,
                'p': i.p,
                'q': i.q,
                'v': i.v,
            } for i in criterio_parametro_queryset])
        else:
            formsQuali = formsetQuali(initial=[{
                'projeto': projeto,
                'criterio': criterio
            } for criterio in criterios])

    if alternativas:
        if len(criterios_quali) > 0:
            df_alternativas = matriz.avaliacoes['alternativas'].to_html()
            pontuacao_alternativas = matriz.pontuacao_alternativas.to_html()
        else:
            pontuacao_alternativas = None
            df_alternativas = None

    if request.method == 'POST':
        CriterioParametro.objects.filter(projeto=projeto).delete()
        formsQuali = formsetQuali(request.POST)
        for form in formsQuali:
            if form.is_valid():
                form.save()
        return redirect('resultado', projeto_id)

    return render(
        request, 'resultado_sapevo.html', {
            'projeto': projeto,
            'pesos': pesos,
            'pontuacao_alternativas': pontuacao_alternativas,
            'valores': valores,
            'df_alternativas': df_alternativas,
            'df_criterios': df_criterios,
            'formsQuali': formsQuali,
        })


def resultado(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    criterios_custo = list(
        Criterio.objects.filter(projeto=projeto, numerico=True,
                                monotonico='2'))
    criterios_custo = [criterio.nome for criterio in criterios_custo]
    parametros = CriterioParametro.objects.filter(projeto=projeto)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    matriz = MatrizProjeto(projeto)

    bn = projeto.qtde_classes
    lamb = projeto.lamb

    if request.method == 'POST':
        projeto.lamb = float(request.POST.get("lamb"))
        lamb = float(request.POST.get("lamb"))

    pesos = matriz.pesos_criterios
    pesos.sort_values(by='peso', ascending=False, inplace=True)
    pesos.rename(columns={
        'Critério': 'Criteria',
        'peso': 'Weight'
    },
        inplace=True)
    pesos = pesos.to_html(index=False)

    valores = AlternativaCriterio.objects.filter(projeto=projeto)
    valores = valores.to_dataframe().to_html()

    if alternativas:
        pontuacao_alternativas = matriz.pontuacao_alternativas

        for criterio in criterios_custo:
            pontuacao_alternativas[
                criterio] = pontuacao_alternativas[criterio] * -1

        parametros = pd.DataFrame(None,
                                  index='p q v w'.split(),
                                  columns=matriz.pesos_criterios['Critério'])

        parametros = CriterioParametro.objects.filter(projeto=projeto)
        parametros = parametros.to_pivot_table(values=['p', 'q', 'v'],
                                               cols=['criterio'])
        parametros.loc['w'] = matriz.pesos_criterios['peso'].values
        parametros.index.rename('parametros')
        electre_quantil = ElectreTri(pontuacao_alternativas,
                                     parametros,
                                     lamb=lamb,
                                     bn=bn,
                                     method='range',
                                     id_projeto=projeto.id)
        df_cla_quantil = electre_quantil.renderizar()
        otimista_quantil, pessimista_quantil = electre_quantil.otimista(
        ).to_frame(name='Otimista'), electre_quantil.pessimista().to_frame(
            name='Pessimista')
        classificacao_quantil = pd.merge(otimista_quantil,
                                         pessimista_quantil,
                                         right_index=True,
                                         left_index=True)

        electre = ElectreTri(pontuacao_alternativas,
                             parametros,
                             lamb=lamb,
                             bn=bn,
                             method='quantile',
                             id_projeto=projeto.id)

        df_cla = electre.renderizar()

        otimista, pessimista = (electre.otimista().to_frame(
            name='Otimista'), electre.pessimista().to_frame(name='Pessimista'))
        classificacao = pd.merge(otimista,
                                 pessimista,
                                 right_index=True,
                                 left_index=True)

        for criterio in criterios_custo:
            pontuacao_alternativas[
                criterio] = pontuacao_alternativas[criterio] * -1
        pontuacao_alternativas = pontuacao_alternativas.to_html()

    else:
        pontuacao_alternativas = None

    classificacao_quantil.rename(columns={
        'Otimista': 'Optimist',
        'Pessimista': 'Pessimist'
    },
        inplace=True)

    classificacao.rename(columns={
        'Otimista': 'Optimist',
        'Pessimista': 'Pessimist'
    },
        inplace=True)

    return render(
        request,
        'resultado.html',
        {
            'projeto': projeto,
            'pesos': pesos,
            'pontuacao_alternativas': pontuacao_alternativas,
            'df_cla_range': classificacao.to_html(),
            'df_cla_quantil': classificacao_quantil.to_html(),
            'projeto': projeto
            # 'df_cla_quantil': df_cla_quantil,
        })


def download_file(request, projeto_id):
    fl_path = f'resultados/result_{projeto_id}.zip'
    filename = f'result_{projeto_id}.zip'

    # opening the 'Zip' in writing mode
    with zipfile.ZipFile(fl_path, 'w') as file:
        # append mode adds files to the 'Zip'
        # you have to create the files which you have to add to the 'Zip'
        file.write(f'resultados/result_bh_{projeto_id}.xlsx',
                   arcname=f'result_bh_{projeto_id}.xlsx')
        file.write(f'resultados/result_bn_{projeto_id}.xlsx',
                   arcname=f'result_bn_{projeto_id}.xlsx')

    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
