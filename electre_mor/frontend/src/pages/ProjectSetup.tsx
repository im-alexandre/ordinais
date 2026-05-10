import { useState, type FormEvent } from 'react';

import { ActionButton } from '../components/ActionButton';
import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { TextField } from '../components/TextField';
import { criarProjeto } from '../services/api';

type ProjectSetupProps = {
  onProjetoCriado?: (projetoId: number) => void;
};

const projetoInicial = {
  nome: '',
  descricao: '',
  qtde_classes: 2,
  qtde_criterios: 2,
  qtde_alternativas: 2,
  qtde_decisores: 1,
  lamb: 0.7,
};

export default function ProjectSetup({ onProjetoCriado }: ProjectSetupProps) {
  const [formulario, setFormulario] = useState(projetoInicial);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  async function lidarComEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setCarregando(true);
    setMensagem(null);

    try {
      const projeto = await criarProjeto(formulario);
      setMensagem(`Projeto ${projeto.nome} criado com sucesso.`);
      onProjetoCriado?.(projeto.id);
    } catch (erro) {
      setMensagem('Nao foi possivel criar o projeto agora.');
    } finally {
      setCarregando(false);
    }
  }

  return (
    <Panel
      titulo="Criar projeto"
      subtitulo="Defina o esqueleto da decisao antes de chamar a API."
    >
      <form className="formulario" onSubmit={lidarComEnvio}>
        <div className="grade-campos">
          <TextField
            label="Nome do projeto"
            value={formulario.nome}
            onChange={(evento) =>
              setFormulario({ ...formulario, nome: evento.target.value })
            }
            required
          />
          <TextField
            label="Descricao"
            value={formulario.descricao}
            onChange={(evento) =>
              setFormulario({ ...formulario, descricao: evento.target.value })
            }
            required
          />
          <TextField
            label="Quantidade de classes"
            type="number"
            min="1"
            value={formulario.qtde_classes}
            onChange={(evento) =>
              setFormulario({
                ...formulario,
                qtde_classes: Number(evento.target.value),
              })
            }
          />
          <TextField
            label="Quantidade de criterios"
            type="number"
            min="1"
            value={formulario.qtde_criterios}
            onChange={(evento) =>
              setFormulario({
                ...formulario,
                qtde_criterios: Number(evento.target.value),
              })
            }
          />
          <TextField
            label="Quantidade de alternativas"
            type="number"
            min="1"
            value={formulario.qtde_alternativas}
            onChange={(evento) =>
              setFormulario({
                ...formulario,
                qtde_alternativas: Number(evento.target.value),
              })
            }
          />
          <TextField
            label="Quantidade de decisores"
            type="number"
            min="1"
            value={formulario.qtde_decisores}
            onChange={(evento) =>
              setFormulario({
                ...formulario,
                qtde_decisores: Number(evento.target.value),
              })
            }
          />
          <TextField
            label="Lambda"
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={formulario.lamb}
            onChange={(evento) =>
              setFormulario({
                ...formulario,
                lamb: Number(evento.target.value),
              })
            }
          />
        </div>
        <div className="formulario-acoes">
          <ActionButton type="submit" disabled={carregando}>
            {carregando ? 'Salvando...' : 'Salvar projeto'}
          </ActionButton>
        </div>
      </form>
      {mensagem ? <Notice variant="success">{mensagem}</Notice> : null}
    </Panel>
  );
}
