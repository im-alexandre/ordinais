import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  criarProjeto,
  gerarResultado,
  listarDecisores,
  obterContextoAvaliacaoPorToken,
  listarProjetos,
  obterResultado,
  salvarParticipantes,
} from './api';
import type { ParticipantesPayload, ResultadoProjeto } from '../types';

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

    const payload: ParticipantesPayload = {
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

  it('resolve o contexto de avaliacao por token', async () => {
    const resposta = {
      project: {
        id: 4,
        nome: 'Projeto X',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 2,
        lamb: 0.65,
      },
      decisor: {
        id: 9,
        nome: 'Ana Souza',
        status: 'pendente',
        ativo: true,
        is_criador: false,
        token: 'token-seguro',
        evaluation_url:
          'http://localhost/?projectId=4&decisorToken=token-seguro&view=avaliacao',
      },
      criterios: [
        { id: 10, nome: 'Qualidade', numerico: false, monotonico: 1 },
      ],
      alternativas: [
        { id: 20, nome: 'Vacina A' },
      ],
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const contexto = await obterContextoAvaliacaoPorToken(4, 'token-seguro');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/evaluation-token/token-seguro/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(contexto).toEqual(resposta);
  });

  it('lista decisores com links individuais de avaliacao', async () => {
    const resposta = [{
      id: 9,
      nome: 'Ana Souza',
      status: 'pendente',
      ativo: true,
      is_criador: false,
      token: 'token-seguro',
      evaluation_url:
        'http://localhost/?projectId=4&decisorToken=token-seguro&view=avaliacao',
    }];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const decisores = await listarDecisores(4);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/decision-makers/',
      expect.objectContaining({
        method: 'GET',
      }),
    );
    expect(decisores).toEqual(resposta);
  });

  it('gera resultado manualmente', async () => {
    const resposta: ResultadoProjeto = {
      project: {
        id: 4,
        nome: 'Projeto X',
        descricao: 'Descricao',
        qtde_classes: 3,
        qtde_criterios: 2,
        qtde_alternativas: 2,
        qtde_decisores: 2,
        lamb: 0.65,
      },
      pesos_criterios: [],
      pontuacao_alternativas: [],
      classificacao_range: [],
      classificacao_quantile: [],
      classificacao_final: {
        range: [],
        quantile: [],
      },
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(resposta), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    vi.stubGlobal('fetch', fetchMock);

    const resultado = await gerarResultado(4);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/projects/4/generate-result/',
      expect.objectContaining({
        method: 'POST',
      }),
    );
    expect(resultado).toEqual(resposta);
  });
});
