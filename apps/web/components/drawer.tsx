'use client';
import { ReactNode } from 'react';

export function Drawer({ open, onClose, children }: { open: boolean; onClose: () => void; children: ReactNode }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex justify-end z-40">
      <div className="bg-white dark:bg-gray-800 w-80 p-4 h-full overflow-y-auto">
        <button onClick={onClose} className="mb-4">Close</button>
        {children}
      </div>
    </div>
  );
}
