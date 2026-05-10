import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import App from './App';

describe('App', () => {
  it('exibe a landing page e navega para a configuracao do projeto', async () => {
    const usuario = userEvent.setup();

    render(<App />);

    expect(
      screen.getByRole('heading', { name: /electre-mor/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/^sapevo-m$/i)).toBeInTheDocument();

    const [botaoConfigurarProjeto] = screen.getAllByRole('button', {
      name: /configurar projeto/i,
    });

    await usuario.click(
      botaoConfigurarProjeto,
    );

    expect(
      screen.getByRole('heading', { name: /criar projeto/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/nome do projeto/i)).toBeInTheDocument();
  });
});
