'use client';
import { ReactNode } from 'react';

export function Modal({
  open,
  onClose,
  children,
}: {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 p-4 rounded">
        <button onClick={onClose} className="mb-4">
          Close
        </button>
        {children}
      </div>
    </div>
  );
}
