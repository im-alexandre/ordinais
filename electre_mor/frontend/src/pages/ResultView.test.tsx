import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import ResultView from './ResultView';
import type { ResultadoProjeto } from '../types';

const mocks = vi.hoisted(() => ({
  obterResultadoMock: vi.fn(),
  gerarResultadoMock: vi.fn(),
  listarDecisoresMock: vi.fn(),
}));

vi.mock('../services/api', () => ({
  obterResultado: mocks.obterResultadoMock,
  gerarResultado: mocks.gerarResultadoMock,
  listarDecisores: mocks.listarDecisoresMock,
}));

const resultadoFinal: ResultadoProjeto = {
  project: {
    id: 4,
    nome: 'Vacinas MOR',
    descricao: 'Analise coletiva',
    qtde_classes: 3,
    qtde_criterios: 2,
    qtde_alternativas: 2,
    qtde_decisores: 2,
    lamb: 0.65,
  },
  pesos_criterios: [
    { criterio: 10, peso: 0.6, criterio_nome: 'Qualidade' },
    { criterio: 11, peso: 0.4, criterio_nome: 'Custo' },
  ],
  pontuacao_alternativas: [],
  classificacao_range: [],
  classificacao_quantile: [],
  classificacao_final: {
    range: [
      {
        alternative_id: 20,
        alternative: 'Vacina A',
        pessimista: 'a1',
        otimista: 'b1',
        class: 'a1',
      },
    ],
    quantile: [
      {
        alternative_id: 20,
        alternative: 'Vacina A',
        pessimista: 'a1',
        otimista: 'b1',
        class: 'a1',
      },
    ],
  },
};

describe('ResultView', () => {
  afterEach(() => {
    mocks.obterResultadoMock.mockReset();
    mocks.gerarResultadoMock.mockReset();
    mocks.listarDecisoresMock.mockReset();
  });

  it('mostra pendencias e desabilita gerar resultado enquanto faltarem decisores', async () => {
    mocks.obterResultadoMock.mockRejectedValueOnce(
      Object.assign(new Error('Resultado ainda nao gerado manualmente.'), {
        status: 409,
        data: {
          detail: 'Resultado ainda nao gerado manualmente.',
          pendencias: [
            {
              id: 9,
              nome: 'Ana Souza',
              status: 'pendente',
              ativo: true,
              faltas: ['notas_numericas'],
            },
          ],
        },
      }),
    );
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);

    render(<ResultView projectId={4} isCreator />);

    expect(
      await screen.findByText(/decisores pendentes/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /gerar resultado/i }),
    ).toBeDisabled();
  });

  it('gera o resultado manualmente quando nao ha pendencias', async () => {
    mocks.obterResultadoMock.mockRejectedValueOnce(
      Object.assign(new Error('Resultado ainda nao gerado manualmente.'), {
        status: 409,
        data: {
          detail: 'Resultado ainda nao gerado manualmente.',
          pendencias: [],
        },
      }),
    );
    mocks.gerarResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);

    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    const botaoGerar = await screen.findByRole('button', {
      name: /gerar resultado/i,
    });

    expect(botaoGerar).toBeEnabled();

    await usuario.click(botaoGerar);

    expect(mocks.gerarResultadoMock).toHaveBeenCalledWith(4);
    expect(
      await screen.findByRole('heading', { name: /classificacao range/i }),
    ).toBeInTheDocument();
  });

  it('mostra o QR de compartilhamento quando o resultado estiver carregado', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);

    render(<ResultView projectId={4} isCreator />);

    expect(
      await screen.findByRole('link', { name: /acessar este projeto/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('img', { name: /qr code/i }),
    ).toBeInTheDocument();
  });

  it('mostra links e qr codes dos decisores convidados para o criador', async () => {
    mocks.obterResultadoMock.mockRejectedValueOnce(
      Object.assign(new Error('Resultado ainda nao gerado manualmente.'), {
        status: 409,
        data: {
          detail: 'Resultado ainda nao gerado manualmente.',
          pendencias: [],
        },
      }),
    );
    mocks.listarDecisoresMock.mockResolvedValueOnce([
      {
        id: 1,
        nome: 'Criador',
        status: 'pendente',
        ativo: true,
        is_criador: true,
        token: 'criador',
        evaluation_url: 'http://localhost/?projectId=4&decisorToken=criador&view=avaliacao',
      },
      {
        id: 2,
        nome: 'Ana Souza',
        status: 'pendente',
        ativo: true,
        is_criador: false,
        token: 'ana',
        evaluation_url: 'http://localhost/?projectId=4&decisorToken=ana&view=avaliacao',
      },
    ]);

    render(<ResultView projectId={4} isCreator />);

    expect(
      await screen.findByRole('heading', { name: /links de avaliacao dos decisores/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/link de avaliacao de ana souza/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('img', { name: /qr code de ana souza/i }),
    ).toBeInTheDocument();
  });
});
