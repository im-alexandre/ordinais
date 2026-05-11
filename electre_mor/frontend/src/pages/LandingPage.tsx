import { useState } from 'react';

import { ActionButton } from '../components/ActionButton';

type LandingPageProps = {
  onConfigurarProjeto: () => void;
  onAbrirFluxo: () => void;
  onAbrirResultado: () => void;
};

async function copiarParaClipboard(texto: string) {
  await navigator.clipboard.writeText(texto);
}

export default function LandingPage({
  onConfigurarProjeto,
  onAbrirFluxo,
  onAbrirResultado,
}: LandingPageProps) {
  const [avisoCitacao, setAvisoCitacao] = useState('');
  const hoje = new Date();
  const dataAcessoPtBr = new Intl.DateTimeFormat('pt-BR').format(hoje);
  const dataAcessoIso = hoje.toISOString().slice(0, 10);
  const citacoes = {
    BibTeX: `@software{costa2026electremor,
  author = {Igor Pinheiro de Araújo Costa and Marcos Alexandre Pinto de Castro Junior and Marcos dos Santos and Carlos Francisco Simões Gomes},
  title = {ELECTRE-MOr Software},
  version = {2},
  year = {2026},
  url = {http://electremor.drg.ink/},
  urldate = {${dataAcessoIso}}
}`,
    ABNT: `COSTA, Igor Pinheiro de Araújo; CASTRO JUNIOR, Marcos Alexandre Pinto de; SANTOS, Marcos dos; GOMES, Carlos Francisco Simões. ELECTRE-MOr Software (v.2). 2026. Disponível em: http://electremor.drg.ink/. Acessado em: ${dataAcessoPtBr}.`,
    '.RIS': `TY  - COMP
TI  - ELECTRE-MOr Software
AU  - Costa, Igor Pinheiro de Araújo
AU  - Castro Junior, Marcos Alexandre Pinto de
AU  - Santos, Marcos dos
AU  - Gomes, Carlos Francisco Simões
PY  - 2026
UR  - http://electremor.drg.ink/
ET  - 2
Y2  - ${dataAcessoIso}
ER  -`,
    APA: `Costa, I. P. de A., Castro Junior, M. A. P. de, Santos, M. dos, & Gomes, C. F. S. (2026). ELECTRE-MOr Software (Version 2) [Computer software]. Retrieved ${dataAcessoIso}, from http://electremor.drg.ink/`,
  };
  const colaboradores = [
    {
      nome: 'Alexandre Castro',
      papel: 'Developer',
      foto: '/static/assets/img/team/2.jpg',
      links: [
        { rotulo: 'GitHub', href: 'https://github.com/im-alexandre' },
        {
          rotulo: 'LinkedIn',
          href: 'https://www.linkedin.com/in/alexandre-castro-45593415a/',
        },
      ],
    },
    {
      nome: 'Prof. Dr. Marcos dos Santos',
      papel: 'Advisor',
      foto: '/static/assets/img/team/3.jpg',
      links: [
        { rotulo: 'Lattes', href: 'http://lattes.cnpq.br/5534398558592175' },
        {
          rotulo: 'LinkedIn',
          href: 'https://www.linkedin.com/in/prof-dr-marcos-santos-67035b1b4/',
        },
      ],
    },
    {
      nome: 'Prof. Dr. Carlos F. Simões Gomes',
      papel: 'Advisor',
      foto: '/static/assets/img/team/4.jpg',
      links: [
        { rotulo: 'Lattes', href: 'http://lattes.cnpq.br/7509084995553647' },
        {
          rotulo: 'LinkedIn',
          href: 'https://linkedin.com/in/carlos-francisco-simões-gomes-7284a3b',
        },
      ],
    },
    {
      nome: 'Igor Pinheiro A. Costa',
      papel: 'Business Analyst',
      foto: '/static/assets/img/team/1.jpg',
      links: [
        { rotulo: 'Lattes', href: 'http://lattes.cnpq.br/1111738924532988' },
        {
          rotulo: 'LinkedIn',
          href: 'https://www.linkedin.com/in/igor-pinheiro-b62a371ab',
        },
      ],
    },
  ];

  async function copiarCitacao(formato: keyof typeof citacoes) {
    await copiarParaClipboard(citacoes[formato]);
    setAvisoCitacao(`${formato} citation copied.`);
  }

  return (
    <main className="landing">
      <section className="hero">
        <h1 className="hero-kicker">ELECTRE-MOr</h1>
        <p className="hero-acronimo">
          <strong>EL</strong>imination <strong>E</strong>t <strong>C</strong>hoix{' '}
          <strong>T</strong>raduisant la <strong>RE</strong>alité -{' '}
          <strong>M</strong>ulticriteria <strong>Or</strong>dinal
        </p>
      </section>

      <section className="equipe" aria-labelledby="equipe-titulo">
        <div className="equipe-cabecalho">
          <h2 id="equipe-titulo" className="hero-kicker equipe-kicker">
            Our team
          </h2>
        </div>
        <div className="equipe-grid">
          {colaboradores.map((colaborador) => (
            <article className="membro" key={colaborador.nome}>
              <img src={colaborador.foto} alt="" className="membro-foto" />
              <h3>{colaborador.nome}</h3>
              <p>{colaborador.papel}</p>
              <div className="membro-links">
                {colaborador.links.map((link) => (
                  <a href={link.href} key={link.href}>
                    {link.rotulo}
                  </a>
                ))}
              </div>
            </article>
          ))}
        </div>
        <div className="citacao">
          <p className="citacao-titulo">
            <strong>To site this software: </strong>
          </p>
          <div className="citacao-acoes" aria-label="Citation formats">
            {(Object.keys(citacoes) as Array<keyof typeof citacoes>).map((formato) => (
              <button type="button" onClick={() => copiarCitacao(formato)} key={formato}>
                {formato}
              </button>
            ))}
          </div>
          {avisoCitacao ? (
            <p className="citacao-aviso" role="status">
              {avisoCitacao}
            </p>
          ) : null}
        </div>
      </section>
    </main>
  );
}
