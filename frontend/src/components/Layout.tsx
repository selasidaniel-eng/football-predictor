import React from 'react'
import './globals.css'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-700">
              ⚽ Football Predictor
            </h1>
            <div className="flex gap-4">
              <a href="/" className="text-gray-600 hover:text-primary-600">
                Home
              </a>
              <a href="/dashboard" className="text-gray-600 hover:text-primary-600">
                Dashboard
              </a>
              <a href="/login" className="text-primary-600 font-medium">
                Login
              </a>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-400">
            © 2024 Football Predictor. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
