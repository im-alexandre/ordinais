import { useEffect, useState } from 'react';

import { Notice } from '../components/Notice';
import { Panel } from '../components/Panel';
import { obterResultado } from '../services/api';
import type { ResultadoProjeto } from '../types';

type ResultViewProps = {
  projectId?: number;
};

export default function ResultView({ projectId }: ResultViewProps) {
  const [resultado, setResultado] = useState<ResultadoProjeto | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (projectId === undefined) {
      return;
    }

    let ativo = true;

    obterResultado(projectId)
      .then((dados) => {
        if (ativo) {
          setResultado(dados);
        }
      })
      .catch(() => {
        if (ativo) {
          setErro('Resultado indisponivel no momento.');
        }
      });

    return () => {
      ativo = false;
    };
  }, [projectId]);

  return (
    <Panel
      titulo="Resultado"
      subtitulo="Resumo executavel da classificacao entregue pela API."
    >
      {erro ? <Notice variant="warning">{erro}</Notice> : null}
      {resultado ? (
        <div className="resultado">
          <p>Projeto: {resultado.project.nome}</p>
          <p>Classes: {resultado.project.qtde_classes}</p>
        </div>
      ) : (
        <Notice variant="info">Nenhum resultado carregado.</Notice>
      )}
    </Panel>
  );
}
