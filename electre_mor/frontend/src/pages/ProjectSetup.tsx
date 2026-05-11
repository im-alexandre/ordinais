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
  qtde_classes: number;
  qtde_criterios: number;
  qtde_alternativas: number;
  qtde_decisores: number;
  lamb: string;
};

const projetoInicial: ProjetoForm = {
  nome: '',
  descricao: '',
  qtde_classes: 3,
  qtde_criterios: 3,
  qtde_alternativas: 5,
  qtde_decisores: 1,
  lamb: '0.65',
};

const nomesCriterios = ['Qualidade', 'Custo', 'Eficacia', 'Logistica', 'Risco'];
const nomesAlternativas = ['Vacina A', 'Vacina B', 'Vacina C', 'Vacina D', 'Vacina E'];

function ajustarTamanho<T>(itens: T[], tamanho: number, criar: (indice: number) => T) {
  if (itens.length === tamanho) {
    return itens;
  }

  if (itens.length > tamanho) {
    return itens.slice(0, tamanho);
  }

  return [...itens, ...Array.from({ length: tamanho - itens.length }, (_, indice) => criar(itens.length + indice))];
}

export default function ProjectSetup({ onProjetoCriado }: ProjectSetupProps) {
  const [formulario, setFormulario] = useState(projetoInicial);
  const [decisores, setDecisores] = useState([{ nome: 'Comite' }]);
  const [criterios, setCriterios] = useState<CriterioEntrada[]>([
    { nome: 'Qualidade', numerico: false, monotonico: 1 },
    { nome: 'Custo', numerico: true, monotonico: 2 },
    { nome: 'Eficacia', numerico: true, monotonico: 1 },
  ]);
  const [alternativas, setAlternativas] = useState(
    nomesAlternativas.map((nome) => ({ nome })),
  );
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  const podeSalvar = useMemo(
    () =>
      formulario.nome.trim() !== '' &&
      formulario.descricao.trim() !== '' &&
      decisores.every((item) => item.nome.trim() !== '') &&
      criterios.every((item) => item.nome.trim() !== '') &&
      alternativas.every((item) => item.nome.trim() !== ''),
    [alternativas, criterios, decisores, formulario.descricao, formulario.nome],
  );

  function atualizarQuantidade(chave: keyof ProjetoForm, valor: number) {
    const quantidade = Math.max(chave === 'qtde_decisores' ? 1 : 2, valor);
    const proximoFormulario = { ...formulario, [chave]: quantidade };
    setFormulario(proximoFormulario);

    if (chave === 'qtde_decisores') {
      setDecisores((atuais) =>
        ajustarTamanho(atuais, quantidade, (indice) => ({
          nome: `Decisor ${indice + 1}`,
        })),
      );
    }

    if (chave === 'qtde_criterios') {
      setCriterios((atuais) =>
        ajustarTamanho(atuais, quantidade, (indice) => ({
          nome: nomesCriterios[indice] ?? `Criterio ${indice + 1}`,
          numerico: indice !== 0,
          monotonico: indice === 1 ? 2 : 1,
        })),
      );
    }

    if (chave === 'qtde_alternativas') {
      setAlternativas((atuais) =>
        ajustarTamanho(atuais, quantidade, (indice) => ({
          nome: nomesAlternativas[indice] ?? `Alternativa ${indice + 1}`,
        })),
      );
    }
  }

  function atualizarLambda(evento: ChangeEvent<HTMLInputElement>) {
    const valorBruto = evento.target.value;

    if (valorBruto === '') {
      setFormulario({ ...formulario, lamb: valorBruto });
      return;
    }

    const valor = Number(valorBruto);
    if (Number.isNaN(valor) || valor < 0.5 || valor > 1) {
      return;
    }

    setFormulario({ ...formulario, lamb: valorBruto });
  }

  async function lidarComEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);

    try {
      const projeto = await criarProjeto({
        ...formulario,
        lamb: Number(formulario.lamb),
      });
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
      subtitulo="Cadastre decisores, criterios e alternativas antes da avaliacao."
    >
      <form className="formulario" onSubmit={lidarComEnvio}>
        <section className="secao-formulario" aria-label="Dados do projeto">
          <div className="grade-campos">
            <TextField
              label="Nome do projeto"
              value={formulario.nome}
              onChange={(evento) =>
                setFormulario({ ...formulario, nome: evento.target.value })
              }
              required
            />
            <TextField
              label="Descricao"
              value={formulario.descricao}
              onChange={(evento) =>
                setFormulario({ ...formulario, descricao: evento.target.value })
              }
              required
            />
            <TextField
              label="Quantidade de classes"
              type="number"
              min="2"
              value={formulario.qtde_classes}
              onChange={(evento) =>
                atualizarQuantidade('qtde_classes', Number(evento.target.value))
              }
            />
            <TextField
              label="Quantidade de criterios"
              type="number"
              min="2"
              value={formulario.qtde_criterios}
              onChange={(evento) =>
                atualizarQuantidade('qtde_criterios', Number(evento.target.value))
              }
            />
            <TextField
              label="Quantidade de alternativas"
              type="number"
              min="2"
              value={formulario.qtde_alternativas}
              onChange={(evento) =>
                atualizarQuantidade('qtde_alternativas', Number(evento.target.value))
              }
            />
            <TextField
              label="Quantidade de decisores"
              type="number"
              min="1"
              value={formulario.qtde_decisores}
              onChange={(evento) =>
                atualizarQuantidade('qtde_decisores', Number(evento.target.value))
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

        <section className="secao-formulario" aria-label="Decisores">
          <h3>Decisores</h3>
          <div className="grade-campos grade-campos-compacta">
            {decisores.map((decisor, indice) => (
              <TextField
                key={indice}
                label={`Decisor ${indice + 1}`}
                value={decisor.nome}
                onChange={(evento) =>
                  setDecisores((atuais) =>
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
          <ActionButton type="submit" disabled={carregando || !podeSalvar}>
            {carregando ? 'Salvando...' : 'Salvar projeto completo'}
          </ActionButton>
        </div>
      </form>
      {mensagem ? <Notice variant="success">{mensagem}</Notice> : null}
    </Panel>
  );
}
