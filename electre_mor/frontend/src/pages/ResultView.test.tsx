import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import ResultView from './ResultView';
import type { ResultadoProjeto } from '../types';

const mocks = vi.hoisted(() => ({
  obterResultadoMock: vi.fn(),
  gerarResultadoMock: vi.fn(),
  listarDecisoresMock: vi.fn(),
  recalcularResultadoMock: vi.fn(),
  xlsx: {
    bookNewMock: vi.fn(() => ({ sheets: [] })),
    aoaToSheetMock: vi.fn((rows: unknown[][]) => ({ rows })),
    bookAppendSheetMock: vi.fn(),
    writeFileMock: vi.fn(),
  },
}));

vi.mock('xlsx', () => ({
  utils: {
    book_new: mocks.xlsx.bookNewMock,
    aoa_to_sheet: mocks.xlsx.aoaToSheetMock,
    book_append_sheet: mocks.xlsx.bookAppendSheetMock,
  },
  writeFile: mocks.xlsx.writeFileMock,
}));

vi.mock('../services/api', () => ({
  obterResultado: mocks.obterResultadoMock,
  gerarResultado: mocks.gerarResultadoMock,
  listarDecisores: mocks.listarDecisoresMock,
  recalcularResultado: mocks.recalcularResultadoMock,
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

const resultadoRecalculado: ResultadoProjeto = {
  project: {
    id: 4,
    nome: 'Vacinas MOR',
    descricao: 'Analise coletiva',
    qtde_classes: 4,
    qtde_criterios: 2,
    qtde_alternativas: 2,
    qtde_decisores: 2,
    lamb: 0.81,
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
        pessimista: 'a2',
        otimista: 'b2',
        class: 'b2',
      },
    ],
    quantile: [
      {
        alternative_id: 20,
        alternative: 'Vacina A',
        pessimista: 'a2',
        otimista: 'b2',
        class: 'b2',
      },
    ],
  },
};

describe('ResultView', () => {
  afterEach(() => {
    mocks.obterResultadoMock.mockReset();
    mocks.gerarResultadoMock.mockReset();
    mocks.listarDecisoresMock.mockReset();
    mocks.recalcularResultadoMock.mockReset();
    mocks.xlsx.bookNewMock.mockClear();
    mocks.xlsx.aoaToSheetMock.mockClear();
    mocks.xlsx.bookAppendSheetMock.mockClear();
    mocks.xlsx.writeFileMock.mockClear();
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
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    expect(
      await screen.findByText(/decisores pendentes/i),
    ).toBeInTheDocument();
    await usuario.click(screen.getByRole('tab', { name: /resultado/i }));
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

    await usuario.click(
      await screen.findByRole('tab', { name: /resultado/i }),
    );

    const botaoGerar = await screen.findByRole('button', {
      name: /gerar resultado/i,
    });

    expect(botaoGerar).toBeEnabled();

    await usuario.click(botaoGerar);

    expect(mocks.gerarResultadoMock).toHaveBeenCalledWith(4);
    expect(
      await screen.findByRole('heading', { name: /classificacao range/i }),
    ).toBeInTheDocument();
    const tabelaRange = screen.getByRole('table', {
      name: /classificacao range/i,
    });

    expect(
      within(tabelaRange).getByRole('columnheader', { name: /alternativa/i }),
    ).toBeInTheDocument();
    expect(
      within(tabelaRange).getByRole('columnheader', { name: /classe pessimista/i }),
    ).toBeInTheDocument();
    expect(
      within(tabelaRange).getByRole('columnheader', { name: /classe otimista/i }),
    ).toBeInTheDocument();
    expect(
      within(tabelaRange).getByRole('columnheader', { name: /^classe$/i }),
    ).toBeInTheDocument();
    expect(
      within(tabelaRange).getByRole('row', { name: /vacina a a1 b1 a1/i }),
    ).toBeInTheDocument();
  });

  it('mostra o QR de compartilhamento quando o resultado estiver carregado', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    expect(
      await screen.findByRole('img', { name: /qr code/i }),
    ).toBeInTheDocument();

    await usuario.click(screen.getByRole('tab', { name: /resultado/i }));

    expect(
      screen.getByRole('link', { name: /acessar este projeto/i }),
    ).toBeInTheDocument();
  });

  it('mostra controles de recálculo apenas para o criador', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([
      {
        id: 1,
        nome: 'Criador',
        status: 'concluido',
        ativo: true,
        is_criador: true,
        token: 'criador-token',
        evaluation_url:
          'http://localhost/?projectId=4&decisorToken=criador-token&view=avaliacao',
      },
    ]);
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    await usuario.click(await screen.findByRole('tab', { name: /resultado/i }));

    expect(await screen.findByLabelText(/lambda oficial/i)).toBeInTheDocument();
    expect(
      await screen.findByLabelText(/n[uú]mero de classes/i),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole('button', { name: /recalcular resultado/i }),
    ).toBeInTheDocument();
  });

  it('bloqueia os controles de recálculo para convidado', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator={false} />);

    await usuario.click(await screen.findByRole('tab', { name: /resultado/i }));

    expect(screen.queryByLabelText(/lambda oficial/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /recalcular resultado/i }),
    ).not.toBeInTheDocument();
  });

  it('recalcula o resultado oficial com decisorToken e atualiza o download xlsx', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([
      {
        id: 1,
        nome: 'Criador',
        status: 'concluido',
        ativo: true,
        is_criador: true,
        token: 'criador-token',
        evaluation_url:
          'http://localhost/?projectId=4&decisorToken=criador-token&view=avaliacao',
      },
    ]);
    mocks.recalcularResultadoMock.mockResolvedValueOnce(resultadoRecalculado);
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    await usuario.click(await screen.findByRole('tab', { name: /resultado/i }));

    const campoLambda = await screen.findByLabelText(/lambda oficial/i);
    const campoClasses = await screen.findByLabelText(/n[uú]mero de classes/i);

    await usuario.clear(campoLambda);
    await usuario.type(campoLambda, '0.81');
    await usuario.clear(campoClasses);
    await usuario.type(campoClasses, '4');
    await usuario.click(
      screen.getByRole('button', { name: /recalcular resultado/i }),
    );

    expect(mocks.recalcularResultadoMock).toHaveBeenCalledWith(4, {
      lambda: 0.81,
      qtde_classes: 4,
      decisorToken: 'criador-token',
    });

    expect(await screen.findByText(/lambda:\s*0\.81/i)).toBeInTheDocument();
    expect(screen.getByText(/classes:\s*4/i)).toBeInTheDocument();

    await usuario.click(
      screen.getByRole('button', { name: /baixar tabela para excel/i }),
    );

    const resumoSheet = mocks.xlsx.aoaToSheetMock.mock.calls[0]?.[0] as unknown[][];
    expect(resumoSheet).toEqual(
      expect.arrayContaining([
        ['Classes', 4],
        ['Lambda', 0.81],
      ]),
    );
    expect(mocks.xlsx.writeFileMock).toHaveBeenCalledWith(
      expect.any(Object),
      'resultado-projeto-4.xlsx',
      { compression: true },
    );
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

  it('baixa o resultado como planilha xlsx', async () => {
    mocks.obterResultadoMock.mockResolvedValueOnce(resultadoFinal);
    mocks.listarDecisoresMock.mockResolvedValueOnce([]);
    const usuario = userEvent.setup();

    render(<ResultView projectId={4} isCreator />);

    await usuario.click(
      await screen.findByRole('tab', { name: /resultado/i }),
    );
    await usuario.click(
      screen.getByRole('button', { name: /baixar tabela para excel/i }),
    );

    expect(mocks.xlsx.writeFileMock).toHaveBeenCalledWith(
      expect.any(Object),
      'resultado-projeto-4.xlsx',
      { compression: true },
    );
    expect(mocks.xlsx.bookAppendSheetMock).toHaveBeenCalledWith(
      expect.any(Object),
      expect.any(Object),
      'Classificacoes',
    );
  });
});
