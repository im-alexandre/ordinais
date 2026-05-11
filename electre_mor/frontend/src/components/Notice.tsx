import type { PropsWithChildren } from 'react';

type NoticeProps = PropsWithChildren<{
  variant?: 'success' | 'info' | 'warning';
}>;

export function Notice({ variant = 'info', children }: NoticeProps) {
  return <div className={`notice notice-${variant}`}>{children}</div>;
}
