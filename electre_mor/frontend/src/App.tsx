import { useState } from 'react';

import { ActionButton } from './components/ActionButton';
import LandingPage from './pages/LandingPage';
import ProjectSetup from './pages/ProjectSetup';
import { EvaluationFlow } from './pages/EvaluationFlow';
import ResultView from './pages/ResultView';
import type { ProjetoCompleto } from './types';

type Tela = 'inicio' | 'setup' | 'avaliacao' | 'resultado';

export default function App() {
  const parametrosUrl = new URLSearchParams(window.location.search);
  const projetoIdInicial = Number(parametrosUrl.get('projectId'));
  const decisorTokenInicial = parametrosUrl.get('decisorToken') ?? undefined;
  const viewInicial = parametrosUrl.get('view');
  const telaInicial =
    viewInicial === 'resultado' && projetoIdInicial > 0
      ? 'resultado'
      : viewInicial === 'setup'
        ? 'setup'
        : viewInicial === 'avaliacao' && projetoIdInicial > 0
          ? 'avaliacao'
      : 'inicio';
  const [tela, setTela] = useState<Tela>(telaInicial);
  const [projeto, setProjeto] = useState<ProjetoCompleto | null>(null);
  const [projetoIdDireto, setProjetoIdDireto] = useState<number | null>(
    projetoIdInicial > 0 ? projetoIdInicial : null,
  );
  const projetoIdAtual = projeto?.projeto.id ?? projetoIdDireto ?? undefined;
  const projetoConfigurado = projeto !== null;
  const podeAbrirFluxos = projetoConfigurado || projetoIdAtual !== undefined;

  function navegar(telaDestino: Tela) {
    if ((telaDestino === 'avaliacao' || telaDestino === 'resultado') && !podeAbrirFluxos) {
      return;
    }

    setTela(telaDestino);
    if (telaDestino === 'resultado') {
      return;
    }

    if (telaDestino === 'setup') {
      window.history.replaceState({}, '', `${window.location.pathname}?view=setup`);
      return;
    }

    window.history.replaceState({}, '', window.location.pathname);
  }

  function abrirResultado(projetoId?: number) {
    const id = projetoId ?? projetoIdAtual;

    if (id === undefined) {
      return;
    }

    setProjetoIdDireto(id);
    window.history.replaceState(
      {},
      '',
      `${window.location.pathname}?projectId=${id}&view=resultado`,
    );
    setTela('resultado');
  }

  return (
    <div className="app-shell">
      <header className="barra-superior">
        <nav className="navegacao">
          <ActionButton
            type="button"
            className={tela === 'inicio' ? '' : 'acao-botao-secundario'}
            onClick={() => navegar('inicio')}
          >
            Início
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'setup' ? '' : 'acao-botao-secundario'}
            onClick={() => navegar('setup')}
          >
            Configurar projeto
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'avaliacao' ? '' : 'acao-botao-secundario'}
            disabled={!podeAbrirFluxos}
            onClick={() => navegar('avaliacao')}
          >
            Avaliar projeto
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'resultado' ? '' : 'acao-botao-secundario'}
            disabled={!podeAbrirFluxos}
            onClick={() => abrirResultado()}
          >
            Resultado
          </ActionButton>
        </nav>
      </header>

      <main className="conteudo-principal">
        {tela === 'inicio' ? (
          <LandingPage
            onConfigurarProjeto={() => setTela('setup')}
            onAbrirFluxo={() => setTela('avaliacao')}
            onAbrirResultado={() => abrirResultado()}
          />
        ) : null}

        {tela === 'setup' ? (
          <ProjectSetup
            onProjetoCriado={(novoProjeto) => {
              setProjeto(novoProjeto);
              setProjetoIdDireto(novoProjeto.projeto.id);
              setTela('avaliacao');
            }}
          />
        ) : null}

        {tela === 'avaliacao' ? (
          <EvaluationFlow
            projeto={projeto}
            projectId={projetoIdAtual}
            decisorToken={decisorTokenInicial}
            onComplete={
              projetoConfigurado ? () => abrirResultado(projetoIdAtual) : undefined
            }
          />
        ) : null}

        {tela === 'resultado' ? (
          <ResultView projectId={projetoIdAtual} isCreator={projetoConfigurado} />
        ) : null}
      </main>
    </div>
  );
}
