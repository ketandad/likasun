'use client';
import { createContext, useContext, useState, ReactNode } from 'react';

interface Toast { id: number; msg: string; }
const ToastContext = createContext<{ push: (msg: string) => void }>({ push: () => {} });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = (msg: string) => setToasts(t => [...t, { id: Date.now(), msg }]);
  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map(t => (
          <div key={t.id} className="bg-gray-800 text-white px-4 py-2 rounded shadow">
            {t.msg}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
