import { useState, type FormEvent } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { TextField } from '../components/TextField';
import { salvarNotasNumericas } from '../services/api';

type EvaluationFlowProps = {
  projectId: number;
  onComplete?: () => void;
};

type LinhaNota = {
  criterio_id: string;
  alternativa_id: string;
  nota: string;
};

export function EvaluationFlow({ projectId, onComplete }: EvaluationFlowProps) {
  const [linha, setLinha] = useState<LinhaNota>({
    criterio_id: '',
    alternativa_id: '',
    nota: '',
  });
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  async function lidarComEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);

    try {
      await salvarNotasNumericas(projectId, {
        scores: [
          {
            criterio_id: Number(linha.criterio_id),
            alternativa_id: Number(linha.alternativa_id),
            nota: Number(linha.nota),
          },
        ],
      });
      setMensagem('Notas numericas salvas.');
      onComplete?.();
    } catch (erro) {
      setMensagem('Nao foi possivel salvar as notas.');
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Panel
      titulo="Fluxo de avaliacao"
      subtitulo={`Projeto em analise: ${projectId}`}
    >
      <form className="formulario" onSubmit={lidarComEnvio}>
        <div className="grade-campos grade-campos-compacta">
          <TextField
            label="Criterio 1"
            type="number"
            min="1"
            value={linha.criterio_id}
            onChange={(evento) =>
              setLinha({ ...linha, criterio_id: evento.target.value })
            }
          />
          <TextField
            label="Alternativa 1"
            type="number"
            min="1"
            value={linha.alternativa_id}
            onChange={(evento) =>
              setLinha({ ...linha, alternativa_id: evento.target.value })
            }
          />
          <TextField
            label="Nota 1"
            type="number"
            step="1"
            min="-2"
            max="10"
            value={linha.nota}
            onChange={(evento) =>
              setLinha({ ...linha, nota: evento.target.value })
            }
          />
        </div>
        <div className="formulario-acoes">
          <ActionButton type="submit" disabled={carregando}>
            {carregando ? 'Enviando...' : 'Salvar notas numericas'}
          </ActionButton>
        </div>
      </form>
      {mensagem ? <Notice variant="success">{mensagem}</Notice> : null}
    </Panel>
  );
}

export default EvaluationFlow;
