import { useState } from 'react';

import { ActionButton } from './components/ActionButton';
import LandingPage from './pages/LandingPage';
import ProjectSetup from './pages/ProjectSetup';
import { EvaluationFlow } from './pages/EvaluationFlow';
import ResultView from './pages/ResultView';

type Tela = 'inicio' | 'setup' | 'avaliacao' | 'resultado';

export default function App() {
  const [tela, setTela] = useState<Tela>('inicio');
  const [projetoId, setProjetoId] = useState<number | null>(null);

  return (
    <div className="app-shell">
      <header className="barra-superior">
        <div>
          <p className="marca">ELECTRE-MOr</p>
          <p className="marca-subtitulo">SAPEVO-M - Método para escolhas firmes.</p>
        </div>
        <nav className="navegacao">
          <ActionButton
            type="button"
            className={tela === 'inicio' ? '' : 'acao-botao-secundario'}
            onClick={() => setTela('inicio')}
          >
            Início
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'setup' ? '' : 'acao-botao-secundario'}
            onClick={() => setTela('setup')}
          >
            Configurar projeto
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'avaliacao' ? '' : 'acao-botao-secundario'}
            onClick={() => setTela('avaliacao')}
          >
            Avaliar projeto
          </ActionButton>
          <ActionButton
            type="button"
            className={tela === 'resultado' ? '' : 'acao-botao-secundario'}
            onClick={() => setTela('resultado')}
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
            onAbrirResultado={() => setTela('resultado')}
          />
        ) : null}

        {tela === 'setup' ? (
          <ProjectSetup onProjetoCriado={(novoProjetoId) => setProjetoId(novoProjetoId)} />
        ) : null}

        {tela === 'avaliacao' ? (
          <EvaluationFlow
            projectId={projetoId ?? 0}
            onComplete={() => setTela('resultado')}
          />
        ) : null}

        {tela === 'resultado' ? <ResultView projectId={projetoId ?? undefined} /> : null}
      </main>
    </div>
  );
}
