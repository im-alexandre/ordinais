import type { InputHTMLAttributes } from 'react';

type TextFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function TextField({
  label,
  id,
  className = '',
  ...props
}: TextFieldProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <label className="campo">
      <span className="campo-rotulo">{label}</span>
      <input
        id={inputId}
        className={`campo-input ${className}`.trim()}
        {...props}
      />
    </label>
  );
}
