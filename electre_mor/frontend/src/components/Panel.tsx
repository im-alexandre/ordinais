import type { PropsWithChildren } from 'react';

type PanelProps = PropsWithChildren<{
  titulo?: string;
  subtitulo?: string;
}>;

export function Panel({ titulo, subtitulo, children }: PanelProps) {
  return (
    <section className="painel">
      {titulo ? <h2 className="painel-titulo">{titulo}</h2> : null}
      {subtitulo ? <p className="painel-subtitulo">{subtitulo}</p> : null}
      <div className="painel-corpo">{children}</div>
    </section>
  );
}
