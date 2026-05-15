import { useMemo, useState, type ChangeEvent, type FormEvent } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { TextField } from '../components/TextField';
import { criarProjeto, salvarParticipantes } from '../services/api';
import type { CriterioEntrada, ProjetoCompleto } from '../types';

type ProjectSetupProps = {
  onProjetoCriado?: (projeto: ProjetoCompleto) => void;
};

type ProjetoForm = {
  nome: string;
  descricao: string;
  qtde_classes: string;
  qtde_criterios: string;
  qtde_alternativas: string;
  qtde_decisores: string;
  lamb: string;
};

type CampoQuantidade =
  | 'qtde_classes'
  | 'qtde_criterios'
  | 'qtde_alternativas'
  | 'qtde_decisores';

type DecisorForm = {
  nome: string;
};

const projetoInicial: ProjetoForm = {
  nome: '',
  descricao: '',
  qtde_classes: '',
  qtde_criterios: '',
  qtde_alternativas: '',
  qtde_decisores: '',
  lamb: '',
};

function ajustarTamanho<T>(
  itens: T[],
  tamanho: number,
  criar: (indice: number) => T,
) {
  if (itens.length === tamanho) {
    return itens;
  }

  if (itens.length > tamanho) {
    return itens.slice(0, tamanho);
  }

  return [
    ...itens,
    ...Array.from({ length: tamanho - itens.length }, (_, indice) =>
      criar(itens.length + indice),
    ),
  ];
}

function normalizarParticipante(nome: string) {
  return nome.trim();
}

export default function ProjectSetup({ onProjetoCriado }: ProjectSetupProps) {
  const [formulario, setFormulario] = useState(projetoInicial);
  const [criador, setCriador] = useState('');
  const [convidados, setConvidados] = useState<DecisorForm[]>([]);
  const [criterios, setCriterios] = useState<CriterioEntrada[]>([]);
  const [alternativas, setAlternativas] = useState<Array<{ nome: string }>>([]);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  const podeSalvar = useMemo(
    () =>
      formulario.nome.trim() !== '' &&
      formulario.descricao.trim() !== '' &&
      formulario.qtde_classes !== '' &&
      formulario.qtde_criterios !== '' &&
      formulario.qtde_alternativas !== '' &&
      formulario.qtde_decisores !== '' &&
      formulario.lamb !== '' &&
      criador.trim() !== '',
    [
      criador,
      formulario.descricao,
      formulario.lamb,
      formulario.nome,
      formulario.qtde_alternativas,
      formulario.qtde_classes,
      formulario.qtde_criterios,
      formulario.qtde_decisores,
    ],
  );

  function atualizarQuantidade(chave: CampoQuantidade, valorBruto: string) {
    if (valorBruto === '') {
      setFormulario((atual) => ({ ...atual, [chave]: '' }));

      if (chave === 'qtde_decisores') {
        setConvidados([]);
      }

      if (chave === 'qtde_criterios') {
        setCriterios([]);
      }

      if (chave === 'qtde_alternativas') {
        setAlternativas([]);
      }

      return;
    }

    const valor = Number(valorBruto);
    if (Number.isNaN(valor)) {
      return;
    }

    const quantidade = Math.max(
      chave === 'qtde_decisores' ? 1 : 2,
      Math.trunc(valor),
    );
    setFormulario((atual) => ({ ...atual, [chave]: String(quantidade) }));

    if (chave === 'qtde_decisores') {
      setConvidados((atuais) =>
        ajustarTamanho(atuais, Math.max(0, quantidade - 1), () => ({
          nome: '',
        })),
      );
    }

    if (chave === 'qtde_criterios') {
      setCriterios((atuais) =>
        ajustarTamanho(atuais, quantidade, (indice) => ({
          nome: `Criterio ${indice + 1}`,
          numerico: indice !== 0,
          monotonico: indice === 1 ? 2 : 1,
        })),
      );
    }

    if (chave === 'qtde_alternativas') {
      setAlternativas((atuais) =>
        ajustarTamanho(atuais, quantidade, (indice) => ({
          nome: `Alternativa ${indice + 1}`,
        })),
      );
    }
  }

  function adicionarDecisor() {
    setConvidados((atuais) => [...atuais, { nome: '' }]);
  }

  function atualizarLambda(evento: ChangeEvent<HTMLInputElement>) {
    const valorBruto = evento.target.value;

    if (valorBruto === '') {
      setFormulario((atual) => ({ ...atual, lamb: valorBruto }));
      return;
    }

    const valor = Number(valorBruto);
    if (Number.isNaN(valor) || valor < 0.5 || valor > 1) {
      return;
    }

    setFormulario((atual) => ({ ...atual, lamb: valorBruto }));
  }

  async function lidarComEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    if (!podeSalvar) {
      setMensagem('Preencha os dados do projeto, o criador e os campos obrigatorios.');
      return;
    }

    setCarregando(true);
    setMensagem(null);

    try {
      const projeto = await criarProjeto({
        nome: formulario.nome,
        descricao: formulario.descricao,
        qtde_classes: Number(formulario.qtde_classes),
        qtde_criterios: Number(formulario.qtde_criterios),
        qtde_alternativas: Number(formulario.qtde_alternativas),
        qtde_decisores: Number(formulario.qtde_decisores),
        lamb: Number(formulario.lamb),
      });

      const decisores = [
        { nome: normalizarParticipante(criador) },
        ...convidados
          .map((item) => normalizarParticipante(item.nome))
          .filter((nome) => nome !== '')
          .map((nome) => ({ nome })),
      ];

      const participantes = await salvarParticipantes(projeto.id, {
        decisores,
        criterios,
        alternativas,
      });

      setMensagem(`Projeto ${projeto.nome} configurado com participantes.`);
      onProjetoCriado?.({
        projeto: participantes.project,
        decisores: participantes.decisores,
        criterios: participantes.criterios,
        alternativas: participantes.alternativas,
      });
    } catch (erro) {
      setMensagem('Nao foi possivel configurar o projeto agora.');
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Panel
      titulo="Configurar projeto"
      subtitulo="Cadastre o criador, convide decisores e avance para a avaliacao sem sair da tela."
    >
      <form className="formulario" onSubmit={lidarComEnvio}>
        <section className="secao-formulario" aria-label="Dados do projeto">
          <div className="grade-campos">
            <TextField
              label="Nome do projeto"
              value={formulario.nome}
              onChange={(evento) =>
                setFormulario((atual) => ({
                  ...atual,
                  nome: evento.target.value,
                }))
              }
              required
            />
            <TextField
              label="Descricao"
              value={formulario.descricao}
              onChange={(evento) =>
                setFormulario((atual) => ({
                  ...atual,
                  descricao: evento.target.value,
                }))
              }
              required
            />
            <TextField
              label="Nome do criador"
              value={criador}
              onChange={(evento) => setCriador(evento.target.value)}
              required
            />
            <TextField
              label="Quantidade de classes"
              type="number"
              min="2"
              value={formulario.qtde_classes}
              onChange={(evento) =>
                atualizarQuantidade('qtde_classes', evento.target.value)
              }
            />
            <TextField
              label="Quantidade de criterios"
              type="number"
              min="2"
              value={formulario.qtde_criterios}
              onChange={(evento) =>
                atualizarQuantidade('qtde_criterios', evento.target.value)
              }
            />
            <TextField
              label="Quantidade de alternativas"
              type="number"
              min="2"
              value={formulario.qtde_alternativas}
              onChange={(evento) =>
                atualizarQuantidade('qtde_alternativas', evento.target.value)
              }
            />
            <TextField
              label="Quantidade de decisores"
              type="number"
              min="1"
              value={formulario.qtde_decisores}
              onChange={(evento) =>
                atualizarQuantidade('qtde_decisores', evento.target.value)
              }
            />
            <TextField
              label="Lambda"
              type="number"
              step="0.01"
              min="0.5"
              max="1"
              value={formulario.lamb}
              onChange={atualizarLambda}
              required
            />
          </div>
        </section>

        <section className="secao-formulario gestao-links" aria-label="Gestao de links">
          <div className="gestao-links-cabecalho">
            <div>
              <h3>Gestao de links</h3>
              <p>
                O criador entra como primeiro decisor e cada convidado pode receber
                um link individual.
              </p>
            </div>
            <ActionButton
              type="button"
              className="acao-botao-secundario"
              onClick={adicionarDecisor}
            >
              Adicionar decisor
            </ActionButton>
          </div>

          <div className="lista-convidados" aria-label="Lista de decisores convidados">
            {convidados.map((decisor, indice) => (
              <TextField
                key={indice}
                label={`Nome do decisor ${indice + 2}`}
                value={decisor.nome}
                onChange={(evento) =>
                  setConvidados((atuais) =>
                    atuais.map((item, itemIndice) =>
                      itemIndice === indice
                        ? { nome: evento.target.value }
                        : item,
                    ),
                  )
                }
              />
            ))}
          </div>
        </section>

        <section className="secao-formulario" aria-label="Decisores">
          <h3>Decisores</h3>
          <div className="gestao-criador">
            <p>
              <strong>Criador principal:</strong>{' '}
              {criador.trim() || 'a definir'}
            </p>
            <p>
              <strong>Convidados preparados:</strong> {convidados.length}
            </p>
          </div>
        </section>

        <section className="secao-formulario" aria-label="Criterios">
          <h3>Criterios</h3>
          <div className="lista-configuracao">
            {criterios.map((criterio, indice) => (
              <div className="linha-configuracao" key={indice}>
                <TextField
                  label={`Criterio ${indice + 1}`}
                  value={criterio.nome}
                  onChange={(evento) =>
                    setCriterios((atuais) =>
                      atuais.map((item, itemIndice) =>
                        itemIndice === indice
                          ? { ...item, nome: evento.target.value }
                          : item,
                      ),
                    )
                  }
                  required
                />
                <label className="campo">
                  <span className="campo-rotulo">Tipo</span>
                  <select
                    className="campo-input"
                    value={criterio.numerico ? 'numerico' : 'qualitativo'}
                    onChange={(evento) =>
                      setCriterios((atuais) =>
                        atuais.map((item, itemIndice) =>
                          itemIndice === indice
                            ? {
                                ...item,
                                numerico: evento.target.value === 'numerico',
                              }
                            : item,
                        ),
                      )
                    }
                  >
                    <option value="qualitativo">Qualitativo</option>
                    <option value="numerico">Numerico</option>
                  </select>
                </label>
                <label className="campo">
                  <span className="campo-rotulo">Direcao</span>
                  <select
                    className="campo-input"
                    value={criterio.monotonico}
                    onChange={(evento) =>
                      setCriterios((atuais) =>
                        atuais.map((item, itemIndice) =>
                          itemIndice === indice
                            ? {
                                ...item,
                                monotonico: Number(evento.target.value) as 1 | 2,
                              }
                            : item,
                        ),
                      )
                    }
                  >
                    <option value={1}>Lucro</option>
                    <option value={2}>Custo</option>
                  </select>
                </label>
              </div>
            ))}
          </div>
        </section>

        <section className="secao-formulario" aria-label="Alternativas">
          <h3>Alternativas</h3>
          <div className="grade-campos grade-campos-compacta">
            {alternativas.map((alternativa, indice) => (
              <TextField
                key={indice}
                label={`Alternativa ${indice + 1}`}
                value={alternativa.nome}
                onChange={(evento) =>
                  setAlternativas((atuais) =>
                    atuais.map((item, itemIndice) =>
                      itemIndice === indice
                        ? { nome: evento.target.value }
                        : item,
                    ),
                  )
                }
                required
              />
            ))}
          </div>
        </section>

        <div className="formulario-acoes">
          <ActionButton type="submit" disabled={carregando}>
            {carregando ? 'Salvando...' : 'Continuar para minha avaliacao'}
          </ActionButton>
        </div>
      </form>
      {mensagem ? <Notice variant="success">{mensagem}</Notice> : null}
    </Panel>
  );
}
