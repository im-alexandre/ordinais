import QRCode from 'qrcode';
import { useEffect, useState } from 'react';

import { ActionButton } from './ActionButton';
import { Notice } from './Notice';

type QrShareCardProps = {
  nome: string;
  url: string;
};

export function QrShareCard({ nome, url }: QrShareCardProps) {
  const [aviso, setAviso] = useState<string | null>(null);
  const [qrDataUrl, setQrDataUrl] = useState('');

  useEffect(() => {
    let ativo = true;

    QRCode.toDataURL(url, {
      errorCorrectionLevel: 'M',
      margin: 2,
      scale: 10,
      color: {
        dark: '#24302d',
        light: '#f8f6f1',
      },
    }).then((dataUrl) => {
      if (ativo) {
        setQrDataUrl(dataUrl);
      }
    });

    return () => {
      ativo = false;
    };
  }, [url]);

  async function copiarLink() {
    await navigator.clipboard?.writeText(url);
    setAviso('Link copiado para a area de transferencia.');
  }

  async function copiarQrCode() {
    if (!qrDataUrl) {
      return;
    }

    if ('ClipboardItem' in window && navigator.clipboard?.write) {
      const resposta = await fetch(qrDataUrl);
      const blob = await resposta.blob();
      await navigator.clipboard.write([
        new ClipboardItem({
          [blob.type]: blob,
        }),
      ]);
      setAviso('QR code copiado para a area de transferencia.');
      return;
    }

    await copiarLink();
  }

  return (
    <article className="qr-share-card">
      <div className="qr-share-card-qr">
        {qrDataUrl ? (
          <img
            alt={`QR Code de ${nome}`}
            className="qr-share-card-image"
            src={qrDataUrl}
          />
        ) : (
          <div aria-label={`QR Code de ${nome}`} className="qr-share-card-placeholder" role="img" />
        )}
      </div>

      <div className="qr-share-card-conteudo">
        <p className="qr-share-card-kicker">Compartilhamento</p>
        <h3>Link de avaliacao de {nome}</h3>
        <p className="qr-share-card-url">{url}</p>

        <div className="qr-share-card-acoes">
          <a className="link-projeto" href={url}>
            Abrir link
          </a>
          <ActionButton type="button" className="acao-botao-secundario" onClick={copiarQrCode}>
            Copiar QR code
          </ActionButton>
          <ActionButton type="button" className="acao-botao-secundario" onClick={copiarLink}>
            Copiar link
          </ActionButton>
        </div>

        {aviso ? (
          <Notice variant="success">{aviso}</Notice>
        ) : null}
      </div>
    </article>
  );
}

export default QrShareCard;
