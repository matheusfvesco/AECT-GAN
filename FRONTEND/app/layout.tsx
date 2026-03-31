import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'X2CT Playground',
  description: 'X-Ray to CT reconstruction playground',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
