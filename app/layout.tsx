import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Vivania - Mining Fleet Management System',
  description: 'Advanced Fleet Management System (FMS) simulator for open pit mining operations',
  metadataBase: new URL(process.env.NEXT_PUBLIC_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'Vivania - Mining Fleet Management System',
    description: 'Advanced Fleet Management System (FMS) simulator for open pit mining operations',
    url: process.env.NEXT_PUBLIC_URL || 'http://localhost:3000',
    siteName: 'Vivania',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Vivania Mining Fleet Management System',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Vivania - Mining Fleet Management System',
    description: 'Advanced Fleet Management System (FMS) simulator for open pit mining operations',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}