import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AECT-GAN Paper Website',
  description: 'AECT-GAN: Adversarial Eulerian CT-GAN for CT synthesis from X-rays',
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
