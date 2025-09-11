'use client';
import { useTheme } from './theme-provider';

export function Header() {
  const { theme, toggle } = useTheme();
  return (
    <header className="p-4 border-b border-gray-700 flex justify-between items-center">
      <span className="font-bold">Compliance Portal</span>
      <button onClick={toggle} aria-label="Toggle theme" className="px-2 py-1 border rounded">
        {theme === 'dark' ? 'Light' : 'Dark'}
      </button>
    </header>
  );
}
