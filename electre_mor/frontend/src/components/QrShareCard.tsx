import { useMemo, useState } from 'react';

import { ActionButton } from './ActionButton';
import { Notice } from './Notice';

type QrShareCardProps = {
  nome: string;
  url: string;
};

type PontoQr = {
  x: number;
  y: number;
};

function hashTexto(texto: string) {
  let hash = 0;
  for (let indice = 0; indice < texto.length; indice += 1) {
    hash = (hash << 5) - hash + texto.charCodeAt(indice);
    hash |= 0;
  }
  return Math.abs(hash);
}

function construirPontosUrl(url: string, tamanho = 21) {
  const pontos: PontoQr[] = [];
  const chaves = new Set<string>();
  const hash = hashTexto(url);

  const reservados = new Set<string>();
  const marcarFinder = (origemX: number, origemY: number) => {
    for (let y = 0; y < 7; y += 1) {
      for (let x = 0; x < 7; x += 1) {
        reservados.add(`${origemX + x}:${origemY + y}`);
      }
    }
  };

  marcarFinder(0, 0);
  marcarFinder(tamanho - 7, 0);
  marcarFinder(0, tamanho - 7);

  for (let linha = 0; linha < tamanho; linha += 1) {
    for (let coluna = 0; coluna < tamanho; coluna += 1) {
      if (reservados.has(`${coluna}:${linha}`)) {
        continue;
      }

      const deslocamento = linha * tamanho + coluna;
      const bit = (hash >> (deslocamento % 31)) ^ (hash >> (deslocamento % 17));
      const chave = `${coluna}:${linha}`;
      if (bit % 3 === 0 && !chaves.has(chave)) {
        chaves.add(chave);
        pontos.push({ x: coluna, y: linha });
      }
    }
  }

  for (let indice = 2; indice < tamanho - 2; indice += 1) {
    if (indice % 2 === 0) {
      for (const ponto of [{ x: 6, y: indice }, { x: indice, y: 6 }]) {
        const chave = `${ponto.x}:${ponto.y}`;
        if (!chaves.has(chave)) {
          chaves.add(chave);
          pontos.push(ponto);
        }
      }
    }
  }

  return pontos;
}

function Ponto({ x, y }: PontoQr) {
  return <rect x={x} y={y} width="1" height="1" rx="0.08" ry="0.08" />;
}

function Finder({ origemX, origemY }: { origemX: number; origemY: number }) {
  return (
    <>
      <rect x={origemX} y={origemY} width="7" height="7" rx="0.5" ry="0.5" fill="none" />
      <rect x={origemX + 1} y={origemY + 1} width="5" height="5" rx="0.35" ry="0.35" />
      <rect x={origemX + 2} y={origemY + 2} width="3" height="3" rx="0.2" ry="0.2" fill="#ffffff" />
    </>
  );
}

export function QrShareCard({ nome, url }: QrShareCardProps) {
  const [copiado, setCopiado] = useState(false);

  const pontos = useMemo(() => construirPontosUrl(url), [url]);

  async function copiarLink() {
    await navigator.clipboard?.writeText(url);
    setCopiado(true);
  }

  return (
    <article className="qr-share-card">
      <div className="qr-share-card-qr">
        <svg
          aria-label={`QR Code de ${nome}`}
          className="qr-share-card-svg"
          viewBox="0 0 21 21"
          role="img"
        >
          <rect width="21" height="21" rx="1.5" ry="1.5" fill="currentColor" className="qr-share-card-background" />
          <g className="qr-share-card-pattern">
            <Finder origemX={0} origemY={0} />
            <Finder origemX={14} origemY={0} />
            <Finder origemX={0} origemY={14} />
            {pontos.map((ponto) => (
              <Ponto key={`${ponto.x}:${ponto.y}`} {...ponto} />
            ))}
          </g>
        </svg>
      </div>

      <div className="qr-share-card-conteudo">
        <p className="qr-share-card-kicker">Compartilhamento</p>
        <h3>Link de avaliacao de {nome}</h3>
        <p className="qr-share-card-url">{url}</p>

        <div className="qr-share-card-acoes">
          <a className="link-projeto" href={url}>
            Abrir link
          </a>
          <ActionButton type="button" className="acao-botao-secundario" onClick={copiarLink}>
            Copiar link
          </ActionButton>
        </div>

        {copiado ? (
          <Notice variant="success">Link copiado para a area de transferencia.</Notice>
        ) : null}
      </div>
    </article>
  );
}

export default QrShareCard;
