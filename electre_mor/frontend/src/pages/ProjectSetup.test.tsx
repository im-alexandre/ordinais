import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ProjectSetup from './ProjectSetup';
import { criarProjeto, salvarParticipantes } from '../services/api';

vi.mock('../services/api', () => ({
  criarProjeto: vi.fn(),
  salvarParticipantes: vi.fn(),
}));

describe('ProjectSetup', () => {
  const criarProjetoMock = vi.mocked(criarProjeto);
  const salvarParticipantesMock = vi.mocked(salvarParticipantes);

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
  });

  it('permite criar projeto com criador como primeiro decisor e continuar para avaliacao', async () => {
    const usuario = userEvent.setup();
    const onProjetoCriado = vi.fn();

    render(<ProjectSetup onProjetoCriado={onProjetoCriado} />);

    await usuario.type(screen.getByLabelText(/nome do projeto/i), 'Vacinas MOR');
    await usuario.type(screen.getByLabelText(/descricao/i), 'Analise coletiva');
    await usuario.type(screen.getByLabelText(/nome do criador/i), 'Alexandre');
    fireEvent.change(screen.getByLabelText(/quantidade de classes/i), {
      target: { value: '3' },
    });
    fireEvent.change(screen.getByLabelText(/quantidade de criterios/i), {
      target: { value: '2' },
    });
    fireEvent.change(screen.getByLabelText(/quantidade de alternativas/i), {
      target: { value: '2' },
    });
    fireEvent.change(screen.getByLabelText(/quantidade de decisores/i), {
      target: { value: '3' },
    });
    fireEvent.change(screen.getByLabelText(/lambda/i), {
      target: { value: '0.65' },
    });

    await usuario.click(
      screen.getByRole('button', { name: /adicionar decisor/i }),
    );
    await usuario.type(screen.getByLabelText(/nome do decisor 2/i), 'Ana Souza');

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
      lamb: 0.65,
    });
    expect(salvarParticipantesMock).toHaveBeenCalledWith(
      41,
      expect.objectContaining({
        decisores: [
          { nome: 'Alexandre' },
          { nome: 'Ana Souza' },
        ],
      }),
    );
    expect(onProjetoCriado).toHaveBeenCalledWith(
      expect.objectContaining({
        projeto: expect.objectContaining({ id: 41 }),
      }),
    );
  });

  it('mostra acao para continuar avaliacao depois de adicionar convidados', () => {
    render(<ProjectSetup onProjetoCriado={vi.fn()} />);

    expect(
      screen.getByRole('button', { name: /adicionar decisor/i }),
    ).toBeEnabled();
    expect(
      screen.getByRole('button', { name: /continuar para minha avaliacao/i }),
    ).toBeEnabled();
  });
});
