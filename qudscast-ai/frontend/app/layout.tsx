import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'QudsCast AI - منصة الأخبار الإذاعية',
  description: 'منصة إعلامية عربية لأتمتة إنتاج الأخبار بالصوت والفيديو',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-arabic antialiased">{children}</body>
    </html>
  );
}
