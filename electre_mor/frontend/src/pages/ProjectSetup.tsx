import { useMemo, useState, type ChangeEvent, type FormEvent } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { TextField } from '../components/TextField';
import {
  baixarPlanilhaModelo,
  confirmarUploadPlanilha,
  criarProjeto,
  preverUploadPlanilha,
  salvarParticipantes,
} from '../services/api';
import type {
  CriterioEntrada,
  OrigemValorPlanilha,
  PlanilhaPreviewResposta,
  ProjetoCompleto,
} from '../types';

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

type Mensagem = {
  texto: string;
  variant: 'success' | 'info' | 'warning';
};

type ParametroChave = 'q' | 'p' | 'v';

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

function rotuloOrigem(origem: OrigemValorPlanilha) {
  switch (origem) {
    case 'automatico':
      return 'Automático';
    case 'planilha':
      return 'Planilha';
    case 'editado':
      return 'Editado';
    default:
      return origem;
  }
}

function formatarValor(valor: number | null) {
  if (valor === null) {
    return '';
  }

  return Number.isInteger(valor) ? String(valor) : String(valor);
}

function todosOsNomesPreenchidos(criterios: CriterioEntrada[], alternativas: Array<{ nome: string }>) {
  return (
    criterios.length > 0 &&
    criterios.every((criterio) => criterio.nome.trim() !== '') &&
    alternativas.length > 0 &&
    alternativas.every((alternativa) => alternativa.nome.trim() !== '')
  );
}

export default function ProjectSetup({ onProjetoCriado }: ProjectSetupProps) {
  const [formulario, setFormulario] = useState(projetoInicial);
  const [criador, setCriador] = useState('');
  const [convidados, setConvidados] = useState<DecisorForm[]>([]);
  const [criterios, setCriterios] = useState<CriterioEntrada[]>([]);
  const [alternativas, setAlternativas] = useState<Array<{ nome: string }>>([]);
  const [projetoSalvo, setProjetoSalvo] = useState<ProjetoCompleto | null>(null);
  const [arquivoPlanilha, setArquivoPlanilha] = useState<File | null>(null);
  const [previewPlanilha, setPreviewPlanilha] =
    useState<PlanilhaPreviewResposta | null>(null);
  const [mensagem, setMensagem] = useState<Mensagem | null>(null);
  const [carregandoProjeto, setCarregandoProjeto] = useState(false);
  const [carregandoPlanilha, setCarregandoPlanilha] = useState(false);
  const [confirmandoUpload, setConfirmandoUpload] = useState(false);

  const podeSalvar = useMemo(
    () =>
      formulario.nome.trim() !== '' &&
      formulario.descricao.trim() !== '' &&
      formulario.qtde_classes !== '' &&
      formulario.qtde_criterios !== '' &&
      formulario.qtde_alternativas !== '' &&
      formulario.qtde_decisores !== '' &&
      criador.trim() !== '',
    [
      criador,
      formulario.descricao,
      formulario.nome,
      formulario.qtde_alternativas,
      formulario.qtde_classes,
      formulario.qtde_criterios,
      formulario.qtde_decisores,
    ],
  );

  const nomesProntos = useMemo(
    () => todosOsNomesPreenchidos(criterios, alternativas),
    [alternativas, criterios],
  );

  const podePrepararPlanilha = podeSalvar && nomesProntos;
  const projetoIdSalvo = projetoSalvo?.projeto.id;

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

  function montarPayloadProjeto() {
    return {
      nome: formulario.nome,
      descricao: formulario.descricao,
      qtde_classes: Number(formulario.qtde_classes),
      qtde_criterios: Number(formulario.qtde_criterios),
      qtde_alternativas: Number(formulario.qtde_alternativas),
      qtde_decisores: Number(formulario.qtde_decisores),
      lamb: formulario.lamb.trim() === '' ? 0.75 : Number(formulario.lamb),
    };
  }

  function montarPayloadParticipantes() {
    const decisores = [
      { nome: normalizarParticipante(criador) },
      ...convidados
        .map((item) => normalizarParticipante(item.nome))
        .filter((nome) => nome !== '')
        .map((nome) => ({ nome })),
    ];

    return {
      decisores,
      criterios,
      alternativas,
    };
  }

  async function garantirProjetoConfigurado() {
    if (projetoSalvo) {
      return projetoSalvo;
    }

    if (!podeSalvar) {
      setMensagem({
        texto: 'Preencha os dados do projeto, o criador e os campos obrigatórios.',
        variant: 'warning',
      });
      return null;
    }

    setCarregandoProjeto(true);
    setMensagem(null);

    try {
      const projeto = await criarProjeto(montarPayloadProjeto());
      const participantes = await salvarParticipantes(
        projeto.id,
        montarPayloadParticipantes(),
      );
      const completo: ProjetoCompleto = {
        projeto: participantes.project,
        decisores: participantes.decisores,
        criterios: participantes.criterios,
        alternativas: participantes.alternativas,
      };

      setProjetoSalvo(completo);
      return completo;
    } catch {
      setMensagem({
        texto: 'Nao foi possivel configurar o projeto agora.',
        variant: 'warning',
      });
      return null;
    } finally {
      setCarregandoProjeto(false);
    }
  }

  async function prepararPlanilha() {
    const completo = await garantirProjetoConfigurado();
    if (!completo) {
      return;
    }

    setMensagem({
      texto: `Projeto ${completo.projeto.nome} pronto para a planilha modelo.`,
      variant: 'info',
    });
  }

  async function continuarParaAvaliacao(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const completo = await garantirProjetoConfigurado();
    if (!completo) {
      return;
    }

    onProjetoCriado?.(completo);
  }

  async function baixarTemplate() {
    if (!projetoIdSalvo) {
      return;
    }

    try {
      const blob = await baixarPlanilhaModelo(projetoIdSalvo);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `planilha-modelo-${projetoIdSalvo}.xlsx`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch {
      setMensagem({
        texto: 'Nao foi possivel baixar a planilha modelo agora.',
        variant: 'warning',
      });
    }
  }

  async function preverPlanilha() {
    if (!projetoIdSalvo || !arquivoPlanilha) {
      setMensagem({
        texto: 'Selecione uma planilha preenchida para revisar antes de confirmar.',
        variant: 'warning',
      });
      return;
    }

    setCarregandoPlanilha(true);
    setMensagem(null);

    try {
      const preview = await preverUploadPlanilha(projetoIdSalvo, arquivoPlanilha);
      setPreviewPlanilha(preview);
    } catch {
      setMensagem({
        texto: 'Nao foi possivel revisar a planilha agora.',
        variant: 'warning',
      });
    } finally {
      setCarregandoPlanilha(false);
    }
  }

  function atualizarParametroPreview(
    criterioId: number,
    chave: ParametroChave,
    valorBruto: string,
  ) {
    setPreviewPlanilha((atual) => {
      if (!atual) {
        return atual;
      }

      const valor = valorBruto.trim() === '' ? null : Number(valorBruto);
      if (valorBruto.trim() !== '' && Number.isNaN(valor)) {
        return atual;
      }

      return {
        ...atual,
        parametros: atual.parametros.map((parametro) =>
          parametro.criterio_id === criterioId
            ? {
                ...parametro,
                [chave]: {
                  valor,
                  origem: 'editado',
                },
              }
            : parametro,
        ),
      };
    });
  }

  async function confirmarPlanilha() {
    if (!projetoIdSalvo || !previewPlanilha) {
      setMensagem({
        texto: 'Revise a planilha antes de confirmar.',
        variant: 'warning',
      });
      return;
    }

    if (previewPlanilha.erros.length > 0) {
      setMensagem({
        texto: 'Corrija os erros da planilha antes de confirmar.',
        variant: 'warning',
      });
      return;
    }

    setConfirmandoUpload(true);
    setMensagem(null);

    try {
      const resultado = await confirmarUploadPlanilha(projetoIdSalvo, {
        desempenhos: previewPlanilha.desempenhos,
        parametros: previewPlanilha.parametros,
      });

      onProjetoCriado?.(resultado);
    } catch {
      setMensagem({
        texto: 'Nao foi possivel confirmar o upload agora.',
        variant: 'warning',
      });
    } finally {
      setConfirmandoUpload(false);
    }
  }

  return (
    <Panel
      titulo="Configurar projeto"
      subtitulo="Cadastre o criador, convide decisores e escolha entre o fluxo manual ou a revisão por planilha."
    >
      <form className="formulario" onSubmit={continuarParaAvaliacao}>
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
              label="Lambda (opcional)"
              type="number"
              step="0.01"
              min="0.5"
              max="1"
              value={formulario.lamb}
              onChange={atualizarLambda}
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

        <section className="secao-formulario planilha-area" aria-label="Planilha">
          <div className="planilha-cabecalho">
            <div>
              <h3>Planilha modelo</h3>
              <p>
                Prepare o projeto, baixe a planilha personalizada e revise o
                arquivo preenchido antes de confirmar o upload.
              </p>
            </div>
            <ActionButton
              type="button"
              className="acao-botao-secundario"
              disabled={!podePrepararPlanilha || carregandoProjeto}
              onClick={prepararPlanilha}
            >
              {carregandoProjeto ? 'Preparando...' : 'Preparar planilha'}
            </ActionButton>
          </div>

          {projetoSalvo ? (
            <div className="planilha-acoes">
              <div className="planilha-acoes-secundarias">
                <p className="planilha-mensagem">
                  Projeto salvo. O download abaixo usa os critérios e alternativas
                  atuais.
                </p>
                <ActionButton
                  type="button"
                  className="acao-botao-secundario"
                  onClick={baixarTemplate}
                >
                  Baixar planilha modelo
                </ActionButton>
              </div>

              <div className="planilha-upload">
                <label className="campo">
                  <span className="campo-rotulo">Planilha preenchida</span>
                  <input
                    aria-label="Planilha preenchida"
                    className="campo-input planilha-upload-input"
                    type="file"
                    accept=".xlsx,.xlsm,.xls"
                    onChange={(evento) => {
                      const arquivo = evento.target.files?.[0] ?? null;
                      setArquivoPlanilha(arquivo);
                      setPreviewPlanilha(null);
                    }}
                  />
                </label>

                <ActionButton
                  type="button"
                  className="acao-botao-secundario"
                  disabled={!arquivoPlanilha || carregandoPlanilha}
                  onClick={preverPlanilha}
                >
                  {carregandoPlanilha ? 'Revisando...' : 'Prever planilha'}
                </ActionButton>
              </div>
            </div>
          ) : null}

          {previewPlanilha ? (
            <section className="planilha-revisao" aria-label="Revisao da planilha">
              <div className="planilha-revisao-cabecalho">
                <div>
                  <h4>Revisão da planilha</h4>
                  <p>
                    Ajuste os parâmetros q, p e v se necessário. Ao editar, a
                    origem passa para editado.
                  </p>
                </div>
                <div className="planilha-revisao-status">
                  {previewPlanilha.erros.length > 0 ? (
                    <Notice variant="warning">
                      Existem erros na planilha. Corrija antes de confirmar.
                    </Notice>
                  ) : null}
                  {previewPlanilha.avisos.length > 0 ? (
                    <Notice variant="info">
                      {previewPlanilha.avisos.map((aviso) => aviso.mensagem).join(' ')}
                    </Notice>
                  ) : null}
                </div>
              </div>

              <div className="planilha-revisao-grid">
                <section className="planilha-revisao-bloco" aria-label="Desempenhos importados">
                  <h5>Desempenhos importados</h5>
                  <ul className="planilha-lista">
                    {previewPlanilha.desempenhos.map((desempenho) => (
                      <li key={desempenho.alternativa_id}>
                        <strong>{desempenho.alternativa}</strong>
                        <span>
                          {desempenho.valores
                            .map((valor) => `${valor.criterio}: ${valor.valor}`)
                            .join(' | ')}
                        </span>
                      </li>
                    ))}
                  </ul>
                </section>

                <section className="planilha-revisao-bloco" aria-label="Parametros da planilha">
                  <h5>Parametros q/p/v</h5>
                  <div className="planilha-parametros">
                    {previewPlanilha.parametros.map((parametro) => (
                      <div className="planilha-parametro-linha" key={parametro.criterio_id}>
                        <div className="planilha-parametro-titulo">{parametro.criterio}</div>
                        {(['q', 'p', 'v'] as const).map((chave) => {
                          const valorParametro = parametro[chave];
                          return (
                            <label
                              className="planilha-parametro-campo"
                              key={`${parametro.criterio_id}-${chave}`}
                            >
                              <span className="campo-rotulo">
                                {chave.toUpperCase()} do {parametro.criterio}
                              </span>
                              <input
                                aria-label={`${chave.toUpperCase()} do ${parametro.criterio}`}
                                className="campo-input planilha-parametro-input"
                                type="number"
                                value={formatarValor(valorParametro.valor)}
                                onChange={(evento) =>
                                  atualizarParametroPreview(
                                    parametro.criterio_id,
                                    chave,
                                    evento.target.value,
                                  )
                                }
                              />
                              <span
                                className={`planilha-origem planilha-origem-${valorParametro.origem}`}
                              >
                                Origem: {rotuloOrigem(valorParametro.origem)}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    ))}
                  </div>
                </section>
              </div>

              <div className="planilha-confirmacao">
                <ActionButton
                  type="button"
                  disabled={confirmandoUpload || previewPlanilha.erros.length > 0}
                  onClick={confirmarPlanilha}
                >
                  {confirmandoUpload ? 'Confirmando...' : 'Confirmar upload e continuar'}
                </ActionButton>
              </div>
            </section>
          ) : null}
        </section>

        <div className="formulario-acoes">
          <ActionButton type="submit" disabled={carregandoProjeto}>
            {carregandoProjeto ? 'Salvando...' : 'Continuar para minha avaliacao'}
          </ActionButton>
        </div>
      </form>

      {mensagem ? <Notice variant={mensagem.variant}>{mensagem.texto}</Notice> : null}
    </Panel>
  );
}
