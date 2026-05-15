import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ProjectSetup from './ProjectSetup';
import {
  baixarPlanilhaModelo,
  confirmarUploadPlanilha,
  criarProjeto,
  preverUploadPlanilha,
  salvarParticipantes,
} from '../services/api';

vi.mock('../services/api', () => ({
  baixarPlanilhaModelo: vi.fn(),
  confirmarUploadPlanilha: vi.fn(),
  criarProjeto: vi.fn(),
  preverUploadPlanilha: vi.fn(),
  salvarParticipantes: vi.fn(),
}));

const criarProjetoMock = vi.mocked(criarProjeto);
const salvarParticipantesMock = vi.mocked(salvarParticipantes);
const baixarPlanilhaModeloMock = vi.mocked(baixarPlanilhaModelo);
const preverUploadPlanilhaMock = vi.mocked(preverUploadPlanilha);
const confirmarUploadPlanilhaMock = vi.mocked(confirmarUploadPlanilha);

function preencherConfigPadrao() {
  return {
    nome: 'Vacinas MOR',
    descricao: 'Analise coletiva',
    criador: 'Alexandre',
    classes: '3',
    criterios: '2',
    alternativas: '2',
    decisores: '3',
    lambda: '0.65',
    convidado: 'Ana Souza',
  };
}

async function preencherFormulario(usuario: ReturnType<typeof userEvent.setup>) {
  const campos = preencherConfigPadrao();

  await usuario.type(screen.getByLabelText(/nome do projeto/i), campos.nome);
  await usuario.type(screen.getByLabelText(/descricao/i), campos.descricao);
  await usuario.type(screen.getByLabelText(/nome do criador/i), campos.criador);
  await usuario.type(
    screen.getByLabelText(/quantidade de classes/i),
    campos.classes,
  );
  await usuario.type(
    screen.getByLabelText(/quantidade de criterios/i),
    campos.criterios,
  );
  await usuario.type(
    screen.getByLabelText(/quantidade de alternativas/i),
    campos.alternativas,
  );
  await usuario.type(
    screen.getByLabelText(/quantidade de decisores/i),
    campos.decisores,
  );
  await usuario.type(screen.getByLabelText(/^lambda/i), campos.lambda);

  await usuario.click(screen.getByRole('button', { name: /adicionar decisor/i }));
  await usuario.type(
    screen.getByLabelText(/nome do decisor 2/i),
    campos.convidado,
  );
}

describe('ProjectSetup', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    criarProjetoMock.mockResolvedValue({
      id: 41,
      nome: 'Vacinas MOR',
      descricao: 'Analise coletiva',
      qtde_classes: 3,
      qtde_criterios: 2,
      qtde_alternativas: 2,
      qtde_decisores: 3,
      lamb: 0.65,
    });

    salvarParticipantesMock.mockResolvedValue({
      project: {
        id: 41,
        nome: 'Vacinas MOR',
        descricao: 'Analise coletiva',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 3,
        lamb: 0.65,
      },
      decisores: [
        {
          id: 1,
          nome: 'Alexandre',
          status: 'pendente',
          ativo: true,
          is_criador: true,
          token: 'alexandre-token',
          evaluation_url:
            'http://localhost/?projectId=41&decisorToken=alexandre-token&view=avaliacao',
        },
        {
          id: 2,
          nome: 'Ana Souza',
          status: 'pendente',
          ativo: true,
          is_criador: false,
          token: 'ana-token',
          evaluation_url:
            'http://localhost/?projectId=41&decisorToken=ana-token&view=avaliacao',
        },
      ],
      criterios: [
        { id: 10, nome: 'Qualidade', numerico: false, monotonico: 1 },
        { id: 11, nome: 'Custo', numerico: true, monotonico: 2 },
      ],
      alternativas: [
        { id: 20, nome: 'A' },
        { id: 21, nome: 'B' },
      ],
    });

    baixarPlanilhaModeloMock.mockResolvedValue(
      new Blob(['xlsx'], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      }),
    );

    preverUploadPlanilhaMock.mockResolvedValue({
      projeto: {
        id: 41,
        nome: 'Vacinas MOR',
        descricao: 'Analise coletiva',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 3,
        lamb: 0.65,
      },
      arquivo: {
        nome: 'vacinas-mor.xlsx',
      },
      desempenhos: [
        {
          alternativa_id: 20,
          alternativa: 'A',
          valores: [
            { criterio_id: 11, criterio: 'Custo', valor: 100 },
          ],
        },
      ],
      parametros: [
        {
          criterio_id: 11,
          criterio: 'Custo',
          q: { valor: 2, origem: 'automatico' },
          p: { valor: 4, origem: 'planilha' },
          v: { valor: 9, origem: 'automatico' },
        },
      ],
      erros: [],
      avisos: [
        {
          codigo: 'parametro_automatico',
          mensagem: 'q calculado automaticamente.',
        },
      ],
    });

    confirmarUploadPlanilhaMock.mockResolvedValue({
      projeto: {
        id: 41,
        nome: 'Vacinas MOR',
        descricao: 'Analise coletiva',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 3,
        lamb: 0.65,
      },
      decisores: [],
      criterios: [],
      alternativas: [],
    });

    Object.defineProperty(window.URL, 'createObjectURL', {
      configurable: true,
      value: vi.fn().mockReturnValue('blob:planilha-modelo'),
    });
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      configurable: true,
      value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
  });

  it('permite continuar com lambda em branco usando o default de 0.75', async () => {
    const usuario = userEvent.setup();
    const onProjetoCriado = vi.fn();

    render(<ProjectSetup onProjetoCriado={onProjetoCriado} />);

    await preencherFormulario(usuario);
    await usuario.clear(screen.getByLabelText(/^lambda/i));

    await usuario.click(
      screen.getByRole('button', { name: /continuar para minha avaliacao/i }),
    );

    expect(criarProjetoMock).toHaveBeenCalledWith({
      nome: 'Vacinas MOR',
      descricao: 'Analise coletiva',
      qtde_classes: 3,
      qtde_criterios: 2,
      qtde_alternativas: 2,
      qtde_decisores: 3,
      lamb: 0.75,
    });
    expect(salvarParticipantesMock).toHaveBeenCalledWith(
      41,
      expect.objectContaining({
        decisores: [{ nome: 'Alexandre' }, { nome: 'Ana Souza' }],
      }),
    );
    expect(onProjetoCriado).toHaveBeenCalledWith(
      expect.objectContaining({
        projeto: expect.objectContaining({ id: 41 }),
      }),
    );
  });

  it('prepara o projeto e permite baixar a planilha modelo personalizada', async () => {
    const usuario = userEvent.setup();

    render(<ProjectSetup onProjetoCriado={vi.fn()} />);

    await preencherFormulario(usuario);
    await usuario.click(
      screen.getByRole('button', { name: /preparar planilha/i }),
    );

    expect(criarProjetoMock).toHaveBeenCalled();
    expect(
      screen.getByRole('button', { name: /baixar planilha modelo/i }),
    ).toBeEnabled();

    await usuario.click(
      screen.getByRole('button', { name: /baixar planilha modelo/i }),
    );

    expect(baixarPlanilhaModeloMock).toHaveBeenCalledWith(41);
    expect(window.URL.createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
  });

  it('exibe a revisão da planilha, permite editar q/p/v e confirma o upload', async () => {
    const usuario = userEvent.setup();
    const onProjetoCriado = vi.fn();

    render(<ProjectSetup onProjetoCriado={onProjetoCriado} />);

    await preencherFormulario(usuario);
    await usuario.click(
      screen.getByRole('button', { name: /preparar planilha/i }),
    );

    const arquivo = new File(['xlsx-binary'], 'vacinas-mor.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    await usuario.upload(
      screen.getByLabelText(/planilha preenchida/i),
      arquivo,
    );
    await usuario.click(
      screen.getByRole('button', { name: /prever planilha/i }),
    );

    expect(preverUploadPlanilhaMock).toHaveBeenCalledWith(41, arquivo);
    expect(
      await screen.findByRole('heading', { name: /revisão da planilha/i }),
    ).toBeInTheDocument();
    expect(screen.getAllByText(/origem: automático/i)).toHaveLength(2);
    expect(screen.getAllByText(/origem: planilha/i)).toHaveLength(1);
    expect(screen.getByText(/custo: 100/i)).toBeInTheDocument();

    const campoQ = screen.getByLabelText(/q do custo/i);
    fireEvent.change(campoQ, { target: { value: '2.5' } });

    expect(campoQ).toHaveValue(2.5);
    expect(campoQ.parentElement?.textContent?.toLowerCase()).toContain(
      'editado',
    );
    expect(screen.getByText(/origem: editado/i)).toBeInTheDocument();

    await usuario.click(
      screen.getByRole('button', { name: /confirmar upload e continuar/i }),
    );

    expect(confirmarUploadPlanilhaMock).toHaveBeenCalledWith(41, {
      desempenhos: [
        {
          alternativa_id: 20,
          alternativa: 'A',
          valores: [
            { criterio_id: 11, criterio: 'Custo', valor: 100 },
          ],
        },
      ],
      parametros: [
        {
          criterio_id: 11,
          criterio: 'Custo',
          q: { valor: 2.5, origem: 'editado' },
          p: { valor: 4, origem: 'planilha' },
          v: { valor: 9, origem: 'automatico' },
        },
      ],
    });
    expect(onProjetoCriado).toHaveBeenCalledWith(
      expect.objectContaining({
        projeto: expect.objectContaining({ id: 41 }),
      }),
    );
  });
});
