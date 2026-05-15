import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { EvaluationFlow } from './EvaluationFlow';
import type { ProjetoCompleto } from '../types';

const mocks = vi.hoisted(() => ({
  obterContextoAvaliacaoPorTokenMock: vi.fn(),
  salvarNotasMock: vi.fn(),
  salvarComparacoesCriteriosMock: vi.fn(),
  salvarComparacoesAlternativasMock: vi.fn(),
  salvarParametrosMock: vi.fn(),
}));

vi.mock('../services/api', () => ({
  obterContextoAvaliacaoPorToken: mocks.obterContextoAvaliacaoPorTokenMock,
  salvarNotasNumericas: mocks.salvarNotasMock,
  salvarComparacoesCriterios: mocks.salvarComparacoesCriteriosMock,
  salvarComparacoesAlternativas: mocks.salvarComparacoesAlternativasMock,
  salvarParametros: mocks.salvarParametrosMock,
}));

const projeto: ProjetoCompleto = {
  projeto: {
    id: 12,
    nome: 'Caso vacina',
    descricao: 'Descricao',
    qtde_classes: 3,
    qtde_criterios: 3,
    qtde_alternativas: 3,
    qtde_decisores: 1,
    lamb: 0.65,
  },
  decisores: [{
    id: 1,
    nome: 'Comite',
    status: 'pendente',
    ativo: true,
    is_criador: true,
    token: 'comite-token',
    evaluation_url:
      'http://localhost/?projectId=12&decisorToken=comite-token&view=avaliacao',
  }],
  criterios: [
    { id: 10, nome: 'Qualidade', numerico: false, monotonico: 1 },
    { id: 11, nome: 'Custo', numerico: true, monotonico: 2 },
    { id: 12, nome: 'Eficacia', numerico: true, monotonico: 1 },
  ],
  alternativas: [
    { id: 20, nome: 'Vacina A' },
    { id: 21, nome: 'Vacina B' },
    { id: 22, nome: 'Vacina C' },
  ],
};

describe('EvaluationFlow', () => {
  afterEach(() => {
    mocks.obterContextoAvaliacaoPorTokenMock.mockReset();
    mocks.salvarNotasMock.mockReset();
    mocks.salvarComparacoesCriteriosMock.mockReset();
    mocks.salvarComparacoesAlternativasMock.mockReset();
    mocks.salvarParametrosMock.mockReset();
  });

  it('envia avaliacao completa para o projeto selecionado', async () => {
    mocks.salvarNotasMock.mockResolvedValue({ project_id: 12, scores: [] });
    mocks.salvarComparacoesCriteriosMock.mockResolvedValue({
      project_id: 12,
      comparisons: [],
    });
    mocks.salvarComparacoesAlternativasMock.mockResolvedValue({
      project_id: 12,
      comparisons: [],
    });
    mocks.salvarParametrosMock.mockResolvedValue({
      project_id: 12,
      parameters: [],
    });

    const usuario = userEvent.setup();

    render(<EvaluationFlow projeto={projeto} />);

    expect(screen.getByLabelText(/avaliador atual/i)).toHaveTextContent(
      /Comite/,
    );

    const [vacinaANoCusto] = screen.getAllByLabelText(/vacina a/i);
    await usuario.clear(vacinaANoCusto);
    await usuario.type(vacinaANoCusto, '40');
    expect(
      screen.getByRole('heading', { name: /avaliações numéricas/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /critérios qualitativos/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/qualidade vs custo/i)).toHaveAttribute(
      'type',
      'range',
    );
    expect(
      screen.getByRole('heading', { name: /avaliações dos critérios/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText(/vacina a vs vacina b/i),
    ).toHaveAttribute('type', 'range');
    await usuario.click(
      screen.getByRole('button', { name: /salvar avaliacao completa/i }),
    );

    expect(mocks.salvarParametrosMock).toHaveBeenCalledWith(12, {
      parameters: expect.arrayContaining([
        expect.objectContaining({ criterio_id: 10, q: 0.1, p: 0.2, v: 0.8 }),
      ]),
    });
    expect(mocks.salvarComparacoesCriteriosMock).toHaveBeenCalledWith(12, {
      comparisons: expect.arrayContaining([
        expect.objectContaining({
          decisor_id: 1,
          criterio_a_id: 10,
          criterio_b_id: 11,
        }),
      ]),
    });
    expect(mocks.salvarNotasMock).toHaveBeenCalledWith(12, {
      scores: expect.arrayContaining([
        { decisor_id: 1, criterio_id: 11, alternativa_id: 20, nota: 40 },
      ]),
    });
    expect(mocks.salvarComparacoesAlternativasMock).toHaveBeenCalledWith(12, {
      comparisons: expect.arrayContaining([
        expect.objectContaining({
          decisor_id: 1,
          criterio_id: 10,
          alternativa_a_id: 20,
          alternativa_b_id: 21,
        }),
      ]),
    });
    expect(
      await screen.findByText(/avaliacao completa salva/i),
    ).toBeInTheDocument();
  });

  it('avalia por token sem mostrar controles de estrutura', async () => {
    mocks.obterContextoAvaliacaoPorTokenMock.mockResolvedValue({
      project: projeto.projeto,
      decisor: {
        id: 9,
        nome: 'Ana Souza',
        status: 'pendente',
        ativo: true,
        is_criador: false,
        token: 'token-seguro',
        evaluation_url:
          'http://localhost/?projectId=12&decisorToken=token-seguro&view=avaliacao',
      },
      criterios: projeto.criterios,
      alternativas: projeto.alternativas,
    });
    mocks.salvarNotasMock.mockResolvedValue({ project_id: 12, scores: [] });
    mocks.salvarComparacoesCriteriosMock.mockResolvedValue({
      project_id: 12,
      comparisons: [],
    });
    mocks.salvarComparacoesAlternativasMock.mockResolvedValue({
      project_id: 12,
      comparisons: [],
    });
    mocks.salvarParametrosMock.mockResolvedValue({
      project_id: 12,
      parameters: [],
    });

    const usuario = userEvent.setup();

    render(
      <EvaluationFlow
        projeto={projeto}
        projectId={12}
        decisorToken="token-seguro"
      />,
    );

    expect(
      await screen.findByText(/fluxo de avaliacao/i),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(/avaliando como ana souza/i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/avaliador atual/i)).toHaveTextContent(
      /Ana Souza/,
    );
    expect(
      screen.queryByRole('button', { name: /configurar projeto/i }),
    ).not.toBeInTheDocument();

    await usuario.click(
      screen.getByRole('button', { name: /salvar avaliacao completa/i }),
    );

    expect(
      mocks.obterContextoAvaliacaoPorTokenMock,
    ).toHaveBeenCalledWith(12, 'token-seguro');
    expect(mocks.salvarComparacoesCriteriosMock).toHaveBeenCalledWith(12, {
      comparisons: expect.arrayContaining([
        expect.objectContaining({
          decisor_id: 9,
        }),
      ]),
    });
  });
});
