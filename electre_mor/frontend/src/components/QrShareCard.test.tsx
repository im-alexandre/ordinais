import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { QrShareCard } from './QrShareCard';

vi.mock('qrcode', () => ({
  default: {
    toDataURL: vi.fn().mockResolvedValue('data:image/png;base64,abc'),
  },
}));

describe('QrShareCard', () => {
  it('renderiza o qr code antes do texto de compartilhamento', async () => {
    render(
      <QrShareCard nome="Ana Souza" url="https://example.test/link" />,
    );

    const qr = await screen.findByRole('img', { name: /qr code/i });
    const titulo = screen.getByText(/link de avaliacao de ana souza/i);

    expect(qr.compareDocumentPosition(titulo) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });

  it('copia o link ao acionar compartilhar', async () => {
    const usuario = userEvent.setup();

    render(
      <QrShareCard nome="Ana Souza" url="https://example.test/link" />,
    );

    await usuario.click(
      screen.getByRole('button', { name: /copiar link/i }),
    );

    expect(
      await screen.findByText(/link copiado para a area de transferencia/i),
    ).toBeInTheDocument();
  });
});
