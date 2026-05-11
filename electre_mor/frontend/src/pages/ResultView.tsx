import { useEffect, useState } from 'react';

import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { obterResultado } from '../services/api';
import type { ResultadoProjeto } from '../types';

type ResultViewProps = {
  projectId?: number;
};

function escaparCsv(valor: unknown) {
  return `"${String(valor ?? '').replace(/"/g, '""')}"`;
}

function montarCsv(resultado: ResultadoProjeto) {
  const linhas = [
    ['Projeto', resultado.project.nome],
    ['Classes', resultado.project.qtde_classes],
    [],
    ['Metodo', 'Alternativa', 'Classe pessimista', 'Classe otimista'],
    ...resultado.classificacao_final.range.map((item) => [
      'range',
      item.alternative,
      item.pessimista,
      item.otimista,
    ]),
    ...resultado.classificacao_final.quantile.map((item) => [
      'quantile',
      item.alternative,
      item.pessimista,
      item.otimista,
    ]),
    [],
    ['Criterio', 'Peso'],
    ...resultado.pesos_criterios.map((item) => [
      item.criterio_nome,
      Number(item.peso).toFixed(6),
    ]),
  ];

  return linhas.map((linha) => linha.map(escaparCsv).join(';')).join('\n');
}

export default function ResultView({ projectId }: ResultViewProps) {
  const [resultado, setResultado] = useState<ResultadoProjeto | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const linkProjeto =
    projectId === undefined
      ? ''
      : `${window.location.origin}${window.location.pathname}?projectId=${projectId}&view=resultado`;

  useEffect(() => {
    if (projectId === undefined) {
      return;
    }

    let ativo = true;

    obterResultado(projectId)
      .then((dados) => {
        if (ativo) {
          setResultado(dados);
          setErro(null);
        }
      })
      .catch(() => {
        if (ativo) {
          setErro('Resultado indisponivel no momento.');
        }
      });

    return () => {
      ativo = false;
    };
  }, [projectId]);

  function baixarTabelaExcel() {
    if (!resultado) {
      return;
    }

    const csv = montarCsv(resultado);
    const arquivo = new Blob([`\ufeff${csv}`], {
      type: 'text/csv;charset=utf-8;',
    });
    const url = URL.createObjectURL(arquivo);
    const link = document.createElement('a');
    link.href = url;
    link.download = `resultado-projeto-${resultado.project.id}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <Panel
      titulo="Resultado"
      subtitulo="Resumo executavel da classificacao entregue pela API."
    >
      {erro ? <Notice variant="warning">{erro}</Notice> : null}
      {resultado ? (
        <div className="resultado">
          <div className="resultado-acoes">
            <a className="link-projeto" href={linkProjeto}>
              Acessar este projeto
            </a>
            <button
              className="acao-botao resultado-botao"
              type="button"
              onClick={baixarTabelaExcel}
            >
              Baixar tabela para Excel
            </button>
          </div>

          <div className="resultado-resumo">
            <p>Projeto: {resultado.project.nome}</p>
            <p>Classes: {resultado.project.qtde_classes}</p>
          </div>

          <div className="resultado-grade">
            <section className="resultado-bloco" aria-label="Classificacao range">
              <h3>Classificacao range</h3>
              <ol>
                {resultado.classificacao_final.range.map((item) => (
                  <li key={`range-${item.alternative_id}`}>
                    <strong>{item.alternative}</strong>
                    <span>{item.pessimista} / {item.otimista}</span>
                  </li>
                ))}
              </ol>
            </section>

            <section className="resultado-bloco" aria-label="Classificacao quantile">
              <h3>Classificacao quantile</h3>
              <ol>
                {resultado.classificacao_final.quantile.map((item) => (
                  <li key={`quantile-${item.alternative_id}`}>
                    <strong>{item.alternative}</strong>
                    <span>{item.pessimista} / {item.otimista}</span>
                  </li>
                ))}
              </ol>
            </section>
          </div>

          <section className="resultado-bloco" aria-label="Pesos dos criterios">
            <h3>Pesos dos criterios</h3>
            <ul>
              {resultado.pesos_criterios.map((item) => (
                <li key={String(item.criterio)}>
                  <strong>{item.criterio_nome}</strong>
                  <span>{Number(item.peso).toFixed(4)}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      ) : (
        <Notice variant="info">Nenhum resultado carregado.</Notice>
      )}
    </Panel>
  );
}
