import { useEffect, useState } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { QrShareCard } from '../components/QrShareCard';
import { gerarResultado, listarDecisores, obterResultado } from '../services/api';
import type { DecisorDetalhado, PendenciaDecisor, ResultadoProjeto } from '../types';

type ResultViewProps = {
  projectId?: number;
  isCreator?: boolean;
};

type XlsxModule = typeof import('xlsx');

function montarWorkbook(resultado: ResultadoProjeto, XLSX: XlsxModule) {
  const workbook = XLSX.utils.book_new();
  const resumo = XLSX.utils.aoa_to_sheet([
    ['Projeto', resultado.project.nome],
    ['Descricao', resultado.project.descricao],
    ['Classes', resultado.project.qtde_classes],
    ['Criterios', resultado.project.qtde_criterios],
    ['Alternativas', resultado.project.qtde_alternativas],
    ['Decisores', resultado.project.qtde_decisores],
    ['Lambda', resultado.project.lamb],
  ]);
  const classificacoes = XLSX.utils.aoa_to_sheet([
    ['Metodo', 'Alternativa', 'Classe pessimista', 'Classe otimista', 'Classe'],
    ...resultado.classificacao_final.range.map((item) => [
      'range',
      item.alternative,
      item.pessimista,
      item.otimista,
      item.class,
    ]),
    ...resultado.classificacao_final.quantile.map((item) => [
      'quantile',
      item.alternative,
      item.pessimista,
      item.otimista,
      item.class,
    ]),
  ]);
  const pesos = XLSX.utils.aoa_to_sheet([
    ['Criterio', 'Peso'],
    ...resultado.pesos_criterios.map((item) => [
      item.criterio_nome,
      Number(item.peso),
    ]),
  ]);

  XLSX.utils.book_append_sheet(workbook, resumo, 'Resumo');
  XLSX.utils.book_append_sheet(workbook, classificacoes, 'Classificacoes');
  XLSX.utils.book_append_sheet(workbook, pesos, 'Pesos');
  return workbook;
}

function isPendenciaApi(erro: unknown) {
  return (
    (typeof erro === 'object' &&
      erro !== null &&
      'status' in erro &&
      Number((erro as { status?: number }).status) === 409)
  );
}

function extrairDadosErro(erro: unknown) {
  if (typeof erro === 'object' && erro !== null && 'data' in erro) {
    return (erro as { data?: unknown }).data;
  }

  return erro;
}

function extrairPendencias(erro: unknown): PendenciaDecisor[] {
  if (!isPendenciaApi(erro)) {
    return [];
  }

  const dados = extrairDadosErro(erro);
  if (typeof dados !== 'object' || dados === null || !('pendencias' in dados)) {
    return [];
  }

  const pendencias = (dados as { pendencias?: PendenciaDecisor[] }).pendencias;
  return Array.isArray(pendencias) ? pendencias : [];
}

function extrairMensagem(erro: unknown) {
  const dados = extrairDadosErro(erro);
  if (typeof dados === 'string') {
    return dados;
  }

  if (typeof dados === 'object' && dados !== null) {
    const detalhes = dados as { detail?: string };
    if (detalhes.detail) {
      return detalhes.detail;
    }
  }

  if (erro instanceof Error) {
    return erro.message;
  }

  return 'Resultado indisponivel no momento.';
}

export default function ResultView({ projectId, isCreator = false }: ResultViewProps) {
  const [resultado, setResultado] = useState<ResultadoProjeto | null>(null);
  const [pendencias, setPendencias] = useState<PendenciaDecisor[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [decisores, setDecisores] = useState<DecisorDetalhado[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [gerando, setGerando] = useState(false);
  const [abaAtiva, setAbaAtiva] = useState<'links' | 'resultado'>('links');
  const linkProjeto =
    projectId === undefined
      ? ''
      : `${window.location.origin}${window.location.pathname}?projectId=${projectId}&view=resultado`;

  useEffect(() => {
    if (projectId === undefined) {
      return;
    }

    let ativo = true;
    setCarregando(true);
    setErro(null);
    setResultado(null);
    setPendencias(null);

    obterResultado(projectId)
      .then((dados) => {
        if (ativo) {
          setResultado(dados);
          setErro(null);
        }
      })
      .catch((error) => {
        if (!ativo) {
          return;
        }

        if (isPendenciaApi(error)) {
          setPendencias(extrairPendencias(error));
          setErro(null);
          return;
        }

        setErro(extrairMensagem(error));
      })
      .finally(() => {
        if (ativo) {
          setCarregando(false);
        }
      });

    return () => {
      ativo = false;
    };
  }, [projectId]);

  useEffect(() => {
    if (!isCreator || projectId === undefined) {
      setDecisores([]);
      return;
    }

    let ativo = true;
    listarDecisores(projectId)
      .then((dados) => {
        if (ativo) {
          setDecisores(dados);
        }
      })
      .catch(() => {
        if (ativo) {
          setDecisores([]);
        }
      });

    return () => {
      ativo = false;
    };
  }, [isCreator, projectId]);

  async function gerarResultadoManual() {
    if (projectId === undefined) {
      return;
    }

    setGerando(true);
    setErro(null);

    try {
      const dados = await gerarResultado(projectId);
      setResultado(dados);
      setPendencias(null);
      setAbaAtiva('resultado');
    } catch (error) {
      if (isPendenciaApi(error)) {
        setPendencias(extrairPendencias(error));
        setErro(null);
      } else {
        setErro(extrairMensagem(error));
      }
    } finally {
      setGerando(false);
    }
  }

  async function baixarTabelaExcel() {
    if (!resultado) {
      return;
    }

    const XLSX = await import('xlsx');
    const workbook = montarWorkbook(resultado, XLSX);
    XLSX.writeFile(workbook, `resultado-projeto-${resultado.project.id}.xlsx`, {
      compression: true,
    });
  }

  const podeGerarResultado =
    isCreator &&
    !gerando &&
    (pendencias === null || pendencias.length === 0) &&
    projectId !== undefined &&
    resultado === null;
  const temLinksDecisores =
    isCreator && decisores.some((decisor) => decisor.ativo && !decisor.is_criador);

  return (
    <Panel
      titulo="Resultado"
      subtitulo="Resumo executavel da classificacao entregue pela API."
    >
      {carregando ? <Notice variant="info">Carregando resultado...</Notice> : null}
      {erro ? <Notice variant="warning">{erro}</Notice> : null}
      <div className="abas-resultado" role="tablist" aria-label="Secoes do resultado">
        <button
          aria-controls="painel-links"
          aria-selected={abaAtiva === 'links'}
          className="aba-resultado"
          id="aba-links"
          onClick={() => setAbaAtiva('links')}
          role="tab"
          type="button"
        >
          Links e QR codes
        </button>
        <button
          aria-controls="painel-resultado"
          aria-selected={abaAtiva === 'resultado'}
          className="aba-resultado"
          id="aba-resultado"
          onClick={() => setAbaAtiva('resultado')}
          role="tab"
          type="button"
        >
          Resultado
        </button>
      </div>

      <div
        aria-labelledby="aba-links"
        hidden={abaAtiva !== 'links'}
        id="painel-links"
        role="tabpanel"
      >
        {projectId !== undefined ? (
          <QrShareCard nome="resultado do projeto" url={linkProjeto} />
        ) : null}
        {temLinksDecisores ? (
          <section className="resultado-bloco links-decisores" aria-label="Links de avaliacao dos decisores">
            <h3>Links de avaliacao dos decisores</h3>
            <div className="links-decisores-grid">
              {decisores
                .filter((decisor) => decisor.ativo && !decisor.is_criador)
                .map((decisor) => (
                  <QrShareCard
                    key={decisor.id}
                    nome={decisor.nome}
                    url={decisor.evaluation_url}
                  />
                ))}
            </div>
          </section>
        ) : null}
      </div>

      <div
        aria-labelledby="aba-resultado"
        hidden={abaAtiva !== 'resultado'}
        id="painel-resultado"
        role="tabpanel"
      >
        {pendencias ? (
          <section className="resultado-bloco resultado-pendencias" aria-label="Decisores pendentes">
            <h3>Decisores pendentes</h3>
            {pendencias.length > 0 ? (
              <ul>
                {pendencias.map((pendencia) => (
                  <li key={String(pendencia.id)}>
                    <strong>{pendencia.nome}</strong>
                    <span>{pendencia.faltas.join(', ') || 'sem pendencias'}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Nenhuma pendencia restante para gerar o resultado.</p>
            )}
            {isCreator ? (
              <div className="resultado-pendencias-acoes">
                <ActionButton
                  type="button"
                  className="resultado-botao"
                  disabled={!podeGerarResultado}
                  onClick={gerarResultadoManual}
                >
                  {gerando ? 'Gerando...' : 'Gerar resultado'}
                </ActionButton>
              </div>
            ) : null}
          </section>
        ) : null}
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
                      <span>
                        {item.pessimista} / {item.otimista}
                      </span>
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
                      <span>
                        {item.pessimista} / {item.otimista}
                      </span>
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
        ) : !pendencias ? (
          <Notice variant="info">Nenhum resultado carregado.</Notice>
        ) : null}
      </div>
    </Panel>
  );
}
