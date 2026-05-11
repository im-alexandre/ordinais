import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  criarProjeto,
  listarProjetos,
  salvarParticipantes,
} from './api';

describe('cliente da API', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('lista projetos a partir de /api/v1/projects/', async () => {
    const resposta = [{ id: 1, nome: 'Projeto A' }];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const projetos = await listarProjetos();

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(projetos).toEqual(resposta);
  });

  it('cria projeto com payload serializado em JSON', async () => {
    const resposta = { id: 9, nome: 'Novo projeto' };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const projeto = await criarProjeto({
      nome: 'Novo projeto',
      descricao: 'Descricao do projeto',
      qtde_classes: 2,
      qtde_criterios: 3,
      qtde_alternativas: 3,
      qtde_decisores: 1,
      lamb: 0.7,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
    expect(projeto).toEqual(resposta);
  });

  it('salva participantes no projeto correto', async () => {
    const resposta = {
      project: { id: 4, nome: 'Projeto X' },
      decisores: [],
      criterios: [],
      alternativas: [],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const payload = {
      decisores: [{ nome: 'Decisor 1' }],
      criterios: [{ nome: 'Criterio 1', numerico: true, monotonico: 1 }],
      alternativas: [{ nome: 'Alternativa 1' }],
    };

    const resultado = await salvarParticipantes(4, payload);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/participants/',
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
    expect(resultado).toEqual(resposta);
  });
});
