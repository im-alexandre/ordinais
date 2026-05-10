import { ActionButton } from '../components/ActionButton';

type LandingPageProps = {
  onConfigurarProjeto: () => void;
  onAbrirFluxo: () => void;
  onAbrirResultado: () => void;
};

export default function LandingPage({
  onConfigurarProjeto,
  onAbrirFluxo,
  onAbrirResultado,
}: LandingPageProps) {
  return (
    <main className="hero">
      <p className="hero-kicker">SAPEVO-M</p>
      <h1>ELECTRE-MOr</h1>
      <p className="hero-copy">
        Start your project! Uma interface premium para estruturar, avaliar e
        classificar alternativas com dados ordinais.
      </p>
      <div className="hero-actions">
        <ActionButton onClick={onConfigurarProjeto}>Configurar projeto</ActionButton>
        <ActionButton onClick={onAbrirFluxo} className="acao-botao-secundario">
          Avaliar projeto
        </ActionButton>
        <ActionButton onClick={onAbrirResultado} className="acao-botao-secundario">
          Ver resultado
        </ActionButton>
      </div>
    </main>
  );
}
