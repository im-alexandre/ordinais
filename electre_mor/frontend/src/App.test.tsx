import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import App from './App';

const apiMocks = vi.hoisted(() => ({
  criarProjeto: vi.fn(),
  gerarResultado: vi.fn(),
  listarDecisores: vi.fn(),
  listarProjetos: vi.fn(),
  obterContextoAvaliacaoPorToken: vi.fn(),
  obterResultado: vi.fn(),
  salvarComparacoesAlternativas: vi.fn(),
  salvarComparacoesCriterios: vi.fn(),
  salvarNotasNumericas: vi.fn(),
  salvarParametros: vi.fn(),
  salvarParticipantes: vi.fn(),
}));

vi.mock('./services/api', () => apiMocks);

describe('App', () => {
  beforeEach(() => {
    Object.values(apiMocks).forEach((mock) => mock.mockReset());
    window.history.replaceState({}, '', window.location.pathname);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    window.history.replaceState({}, '', window.location.pathname);
  });

  it('exibe a landing page e navega para a configuracao do projeto', async () => {
    const usuario = userEvent.setup();

    render(<App />);

    expect(screen.getByText(/imination/i)).toBeInTheDocument();
    expect(screen.getByText(/alexandre castro/i)).toBeInTheDocument();
    expect(screen.getByText(/igor pinheiro/i)).toBeInTheDocument();

    const botaoConfigurarProjeto = screen.getAllByRole('button', {
      name: /configurar projeto/i,
    })[0];

    await usuario.click(botaoConfigurarProjeto);

    expect(
      screen.getByRole('heading', { name: /configurar projeto/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/nome do criador/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/nome do projeto/i)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /adicionar decisor/i }),
    ).toBeEnabled();
  });

  it('copia a citacao no formato selecionado', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    const usuario = userEvent.setup();
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    });

    render(<App />);

    await usuario.click(screen.getByRole('button', { name: /bibtex/i }));

    expect(
      await screen.findByText(/bibtex citation copied/i),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(
        expect.stringContaining('costa2026electremor'),
      );
      expect(writeText).toHaveBeenCalledWith(
        expect.stringContaining('http://electremor.drg.ink/'),
      );
    });
  });

  it('bloqueia valores de lambda fora do intervalo entre 0.5 e 1', async () => {
    const usuario = userEvent.setup();

    render(<App />);

    const [botaoConfigurarProjeto] = screen.getAllByRole('button', {
      name: /configurar projeto/i,
    });

    await usuario.click(botaoConfigurarProjeto);

    const campoLambda = screen.getByLabelText(/lambda/i);

    expect(campoLambda).toHaveValue(null);

    fireEvent.change(campoLambda, { target: { value: '1.5' } });

    expect(campoLambda).toHaveValue(null);

    fireEvent.change(campoLambda, { target: { value: '0.49' } });

    expect(campoLambda).toHaveValue(null);

    fireEvent.change(campoLambda, { target: { value: '0.6' } });

    expect(campoLambda).toHaveValue(0.6);
  });

  it('abre o fluxo de avaliacao com token pela URL sem projeto em memoria', async () => {
    apiMocks.obterContextoAvaliacaoPorToken.mockResolvedValueOnce({
      project: {
        id: 12,
        nome: 'Projeto Token',
        descricao: 'Descricao de teste',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 1,
        lamb: 0.7,
      },
      decisor: {
        id: 34,
        nome: 'Decisor Token',
        status: 'em_edicao',
        ativo: true,
        is_criador: false,
        token: 'abc',
        evaluation_url: 'http://localhost/?projectId=12&decisorToken=abc&view=avaliacao',
      },
      criterios: [
        { id: 10, nome: 'Qualidade', numerico: false, monotonico: 1 },
        { id: 11, nome: 'Custo', numerico: true, monotonico: 2 },
      ],
      alternativas: [
        { id: 20, nome: 'Vacina A' },
        { id: 21, nome: 'Vacina B' },
      ],
    });

    window.history.replaceState(
      {},
      '',
      '/?projectId=12&decisorToken=abc&view=avaliacao',
    );

    render(<App />);

    expect(
      await screen.findByText(/avaliando como decisor token\./i),
    ).toBeInTheDocument();
    expect(apiMocks.obterContextoAvaliacaoPorToken).toHaveBeenCalledWith(
      12,
      'abc',
    );
  });

  it('mantem avaliacao e resultado bloqueados ate configurar o projeto', () => {
    render(<App />);

    expect(
      screen.getByRole('button', { name: /avaliar projeto/i }),
    ).toBeDisabled();
    expect(screen.getByRole('button', { name: /resultado/i })).toBeDisabled();
  });
});
