import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { EvaluationFlow } from './EvaluationFlow';

const { salvarNotasMock } = vi.hoisted(() => ({
  salvarNotasMock: vi.fn(),
}));

vi.mock('../services/api', () => ({
  salvarNotasNumericas: salvarNotasMock,
}));

describe('EvaluationFlow', () => {
  afterEach(() => {
    salvarNotasMock.mockReset();
  });

  it('enviar notas numericas para o projeto selecionado', async () => {
    salvarNotasMock.mockResolvedValue({
      project_id: 12,
      scores: [{ criterio_id: 1, alternativa_id: 2, nota: 7 }],
    });

    const usuario = userEvent.setup();

    render(<EvaluationFlow projectId={12} />);

    await usuario.clear(screen.getByLabelText(/criterio 1/i));
    await usuario.type(screen.getByLabelText(/criterio 1/i), '1');
    await usuario.clear(screen.getByLabelText(/alternativa 1/i));
    await usuario.type(screen.getByLabelText(/alternativa 1/i), '2');
    await usuario.clear(screen.getByLabelText(/nota 1/i));
    await usuario.type(screen.getByLabelText(/nota 1/i), '7');
    await usuario.click(
      screen.getByRole('button', { name: /salvar notas numericas/i }),
    );

    expect(salvarNotasMock).toHaveBeenCalledWith(12, {
      scores: [{ criterio_id: 1, alternativa_id: 2, nota: 7 }],
    });
    expect(
      await screen.findByText(/notas numericas salvas/i),
    ).toBeInTheDocument();
  });
});
