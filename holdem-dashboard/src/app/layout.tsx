import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Holdem Agent Dashboard",
  description: "Real-time statistics dashboard for Texas Hold'em poker agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <h1 className="text-xl font-bold text-gray-900">
                      🎰 Holdem Agent Dashboard
                    </h1>
                  </div>
                  <div className="hidden md:ml-10 md:flex md:space-x-8">
                    <Link
                      href="/"
                      className="text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Dashboard
                    </Link>
                    <Link
                      href="/performance"
                      className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Performance
                    </Link>
                    <Link
                      href="/hands"
                      className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Hand History
                    </Link>
                    <Link
                      href="/settings"
                      className="text-gray-500 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Settings
                    </Link>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Agent Online</span>
                  </div>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
