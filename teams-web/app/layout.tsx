import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/components/global.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Teams AI - AI Workforce for Your Business',
  description: 'An army of AI agents that work together to deliver results for small businesses, solopreneurs, and freelancers.',
  keywords: ['AI', 'Teams', 'Agents', 'Workforce', 'Business', 'Small Business', 'Solopreneur', 'Freelancer'],
  icons: {
    icon: '/favicon.ico',
  },
  authors: [
    { name: 'Aman', url: 'https://amankumar.ai' },
  ]
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
