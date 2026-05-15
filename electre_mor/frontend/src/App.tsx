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
  const viewInicial = parametrosUrl.get('view');
  const telaInicial =
    viewInicial === 'resultado' && projetoIdInicial > 0
      ? 'resultado'
      : viewInicial === 'setup'
        ? 'setup'
      : 'inicio';
  const [tela, setTela] = useState<Tela>(telaInicial);
  const [projeto, setProjeto] = useState<ProjetoCompleto | null>(null);
  const [projetoIdDireto, setProjetoIdDireto] = useState<number | null>(
    projetoIdInicial > 0 ? projetoIdInicial : null,
  );
  const projetoConfigurado = projeto !== null;

  function navegar(telaDestino: Tela) {
    if (
      (telaDestino === 'avaliacao' || telaDestino === 'resultado') &&
      !projetoConfigurado
    ) {
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
    if (!projetoConfigurado) {
      return;
    }

    const id = projetoId ?? projeto?.projeto.id ?? projetoIdDireto;
    if (id !== null && id !== undefined) {
      setProjetoIdDireto(id);
      window.history.replaceState(
        {},
        '',
        `${window.location.pathname}?projectId=${id}&view=resultado`,
      );
    }
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
            disabled={!projetoConfigurado}
            onClick={() => navegar('avaliacao')}
          >
            Avaliar projeto
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'resultado' ? '' : 'acao-botao-secundario'}
            disabled={!projetoConfigurado}
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
            onComplete={() => abrirResultado(projeto?.projeto.id)}
          />
        ) : null}

        {tela === 'resultado' ? (
          <ResultView projectId={projeto?.projeto.id ?? projetoIdDireto ?? undefined} />
        ) : null}
      </main>
    </div>
  );
}
