import './globals.css';
import { ReactNode } from 'react';
import { ThemeProvider } from '../components/theme-provider';
import { Header } from '../components/header';
import { ToastProvider } from '../components/toast';

export const metadata = { title: 'Compliance Portal' };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <ToastProvider>
            <Header />
            <main className="p-4">{children}</main>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
