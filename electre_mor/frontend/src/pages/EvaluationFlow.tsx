import { useMemo, useState, type FormEvent } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { TextField } from '../components/TextField';
import {
  salvarComparacoesAlternativas,
  salvarComparacoesCriterios,
  salvarNotasNumericas,
  salvarParametros,
} from '../services/api';
import type { ProjetoCompleto } from '../types';

type EvaluationFlowProps = {
  projeto?: ProjetoCompleto | null;
  projectId?: number;
  onComplete?: () => void;
};

type Par = {
  a: number;
  b: number;
};

function pares<T>(itens: T[]): Par[] {
  return itens.flatMap((_, indiceA) =>
    itens.slice(indiceA + 1).map((_, indiceRelativo) => ({
      a: indiceA,
      b: indiceA + indiceRelativo + 1,
    })),
  );
}

function notaPadrao(indiceA: number, indiceB: number) {
  return Math.min(2, Math.max(-2, indiceB - indiceA));
}

type ComparacaoSliderProps = {
  esquerda: string;
  direita: string;
  nota: string;
  onChange: (nota: string) => void;
  rotulo?: string;
  compacto?: boolean;
};

function ComparacaoSlider({
  esquerda,
  direita,
  nota,
  onChange,
  rotulo,
  compacto = false,
}: ComparacaoSliderProps) {
  const nomeAcessivel = rotulo ?? `${esquerda} vs ${direita}`;
  const valorVisual = String(-Number(nota));

  return (
    <label
      className={`comparacao-slider ${compacto ? 'comparacao-slider-compacto' : ''}`.trim()}
    >
      {rotulo ? <span className="comparacao-slider-rotulo">{rotulo}</span> : null}
      <span className="comparacao-slider-controle">
        <span>{esquerda}</span>
        <input
          aria-label={nomeAcessivel}
          className="comparacao-slider-input"
          type="range"
          min="-2"
          max="2"
          step="1"
          value={valorVisual}
          onChange={(evento) => onChange(String(-Number(evento.target.value)))}
        />
        <span>{direita}</span>
      </span>
    </label>
  );
}

export function EvaluationFlow({
  projeto,
  projectId,
  onComplete,
}: EvaluationFlowProps) {
  const projetoId = projeto?.projeto.id ?? projectId ?? 0;
  const criterios = projeto?.criterios ?? [];
  const alternativas = projeto?.alternativas ?? [];
  const decisorId = projeto?.decisores[0]?.id ?? 0;
  const criteriosNumericos = criterios.filter((criterio) => criterio.numerico);
  const criteriosQualitativos = criterios.filter((criterio) => !criterio.numerico);

  const paresCriterios = useMemo(() => pares(criterios), [criterios]);
  const paresAlternativas = useMemo(() => pares(alternativas), [alternativas]);

  const [notasNumericas, setNotasNumericas] = useState<Record<string, string>>({});
  const [comparacoesCriterios, setComparacoesCriterios] = useState<Record<string, string>>({});
  const [comparacoesAlternativas, setComparacoesAlternativas] = useState<Record<string, string>>({});
  const [parametros, setParametros] = useState<Record<string, { q: string; p: string; v: string }>>({});
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  function valorNotaNumerica(criterioIndice: number, alternativaIndice: number) {
    const chave = `${criterioIndice}:${alternativaIndice}`;
    if (notasNumericas[chave] !== undefined) {
      return notasNumericas[chave];
    }

    const valoresExemplo = [
      [42, 35, 55, 48, 39],
      [91, 86, 94, 88, 90],
      [7, 8, 6, 7, 9],
    ];
    return String(
      valoresExemplo[criterioIndice]?.[alternativaIndice] ??
        (criterioIndice + 1) * 10 + alternativaIndice,
    );
  }

  function valorComparacaoCriterio(indiceA: number, indiceB: number) {
    const chave = `${indiceA}:${indiceB}`;
    return comparacoesCriterios[chave] ?? String(notaPadrao(indiceA, indiceB));
  }

  function valorComparacaoAlternativa(
    criterioId: number,
    indiceA: number,
    indiceB: number,
  ) {
    const chave = `${criterioId}:${indiceA}:${indiceB}`;
    return comparacoesAlternativas[chave] ?? String(notaPadrao(indiceA, indiceB));
  }

  function valorParametro(criterioId: number, chave: 'q' | 'p' | 'v') {
    return parametros[String(criterioId)]?.[chave] ?? { q: '0.1', p: '0.2', v: '0.8' }[chave];
  }

  async function lidarComEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    if (!projeto || decisorId === 0) {
      setMensagem('Configure o projeto antes de avaliar.');
      return;
    }

    setCarregando(true);
    setMensagem(null);

    try {
      await salvarParametros(projetoId, {
        parameters: criterios.map((criterio) => ({
          criterio_id: criterio.id,
          q: Number(valorParametro(criterio.id, 'q')),
          p: Number(valorParametro(criterio.id, 'p')),
          v: Number(valorParametro(criterio.id, 'v')),
        })),
      });

      await salvarComparacoesCriterios(projetoId, {
        comparisons: paresCriterios.map((par) => ({
          decisor_id: decisorId,
          criterio_a_id: criterios[par.a].id,
          criterio_b_id: criterios[par.b].id,
          nota: Number(valorComparacaoCriterio(par.a, par.b)),
        })),
      });

      await salvarNotasNumericas(projetoId, {
        scores: criteriosNumericos.flatMap((criterio, criterioIndice) =>
          alternativas.map((alternativa, alternativaIndice) => ({
            decisor_id: decisorId,
            criterio_id: criterio.id,
            alternativa_id: alternativa.id,
            nota: Number(valorNotaNumerica(criterioIndice, alternativaIndice)),
          })),
        ),
      });

      await salvarComparacoesAlternativas(projetoId, {
        comparisons: criteriosQualitativos.flatMap((criterio) =>
          paresAlternativas.map((par) => ({
            decisor_id: decisorId,
            criterio_id: criterio.id,
            alternativa_a_id: alternativas[par.a].id,
            alternativa_b_id: alternativas[par.b].id,
            nota: Number(valorComparacaoAlternativa(criterio.id, par.a, par.b)),
          })),
        ),
      });

      setMensagem('Avaliacao completa salva.');
      onComplete?.();
    } catch (erro) {
      setMensagem('Nao foi possivel salvar a avaliacao completa.');
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Panel
      titulo="Fluxo de avaliacao"
      subtitulo={`Projeto em analise: ${projetoId || 'nao configurado'}`}
    >
      {!projeto ? (
        <Notice variant="warning">Configure o projeto antes de avaliar.</Notice>
      ) : null}

      <form className="formulario" onSubmit={lidarComEnvio}>
        <div className="painel-avaliacao-topo">
          <section className="avaliacao-card" aria-label="Parametros q p v">
            <h3>Parametros q, p e v</h3>
            <div className="tabela-parametros" role="table">
              <div className="tabela-parametros-cabecalho" role="row">
                <span>Criterio</span>
                <span>q</span>
                <span>p</span>
                <span>v</span>
              </div>
              {criterios.map((criterio) => (
                <div className="tabela-parametros-linha" role="row" key={criterio.id}>
                  <span>{criterio.nome}</span>
                  {(['q', 'p', 'v'] as const).map((chave) => (
                    <input
                      key={chave}
                      aria-label={`${criterio.nome} ${chave}`}
                      className="campo-input campo-input-compacto"
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={valorParametro(criterio.id, chave)}
                      onChange={(evento) =>
                        setParametros((atuais) => ({
                          ...atuais,
                          [criterio.id]: {
                            q: valorParametro(criterio.id, 'q'),
                            p: valorParametro(criterio.id, 'p'),
                            v: valorParametro(criterio.id, 'v'),
                            [chave]: evento.target.value,
                          },
                        }))
                      }
                    />
                  ))}
                </div>
              ))}
            </div>
          </section>

          <section className="avaliacao-card" aria-label="Avaliações dos Critérios">
            <h3>Avaliações dos Critérios</h3>
            <div className="grade-comparacoes-criterios">
              {paresCriterios.map((par) => (
                <ComparacaoSlider
                  key={`${par.a}:${par.b}`}
                  esquerda={criterios[par.a].nome}
                  direita={criterios[par.b].nome}
                  nota={valorComparacaoCriterio(par.a, par.b)}
                  onChange={(nota) =>
                    setComparacoesCriterios((atuais) => ({
                      ...atuais,
                      [`${par.a}:${par.b}`]: nota,
                    }))
                  }
                />
              ))}
            </div>
          </section>
        </div>

        <section className="secao-formulario" aria-label="Avaliações numéricas">
          <h3>Avaliações Numéricas:</h3>
          <div className="criterios-avaliacao">
            {criteriosNumericos.map((criterio, criterioIndice) => (
              <section className="criterio-avaliacao" key={criterio.id}>
                <h4>{criterio.nome}:</h4>
                <div className="grade-avaliacoes">
                  {alternativas.map((alternativa, alternativaIndice) => (
                    <TextField
                      key={`${criterio.id}:${alternativa.id}`}
                      label={alternativa.nome}
                      type="number"
                      step="0.1"
                      value={valorNotaNumerica(criterioIndice, alternativaIndice)}
                      onChange={(evento) =>
                        setNotasNumericas((atuais) => ({
                          ...atuais,
                          [`${criterioIndice}:${alternativaIndice}`]:
                            evento.target.value,
                        }))
                      }
                    />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </section>

        <section className="secao-formulario" aria-label="Critérios qualitativos">
          <h3>Critérios qualitativos:</h3>
          <div className="criterios-avaliacao">
            {criteriosQualitativos.map((criterio) => (
              <section className="criterio-avaliacao" key={criterio.id}>
                <h4>{criterio.nome}:</h4>
                <div className="grade-comparacoes">
                  {paresAlternativas.map((par) => (
                    <ComparacaoSlider
                      key={`${criterio.id}:${par.a}:${par.b}`}
                      esquerda={alternativas[par.a].nome}
                      direita={alternativas[par.b].nome}
                      nota={valorComparacaoAlternativa(criterio.id, par.a, par.b)}
                      onChange={(nota) =>
                        setComparacoesAlternativas((atuais) => ({
                          ...atuais,
                          [`${criterio.id}:${par.a}:${par.b}`]: nota,
                        }))
                      }
                    />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </section>

        <div className="formulario-acoes">
          <ActionButton type="submit" disabled={carregando || !projeto}>
            {carregando ? 'Salvando...' : 'Salvar avaliacao completa'}
          </ActionButton>
        </div>
      </form>
      {mensagem ? <Notice variant={mensagem.includes('Nao') || mensagem.includes('Configure') ? 'warning' : 'success'}>{mensagem}</Notice> : null}
    </Panel>
  );
}

export default EvaluationFlow;
