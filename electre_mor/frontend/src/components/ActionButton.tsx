import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';

type ActionButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement>
>;

export function ActionButton({
  children,
  className = '',
  ...props
}: ActionButtonProps) {
  return (
    <button className={`acao-botao ${className}`.trim()} {...props}>
      {children}
    </button>
  );
}
