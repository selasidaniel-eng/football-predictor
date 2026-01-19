import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/hooks/useAuth'
import { Layout } from '@/components/Layout'

// Page imports (TODO: Create these pages)
// import HomePage from '@/pages/HomePage'
// import DashboardPage from '@/pages/DashboardPage'
// import MatchDetailPage from '@/pages/MatchDetailPage'
// import LoginPage from '@/pages/LoginPage'
// import RegisterPage from '@/pages/RegisterPage'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            {/* <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/match/:id" element={<MatchDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} /> */}
            
            {/* Placeholder route */}
            <Route 
              path="/" 
              element={
                <div className="text-center py-12">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    ⚽ Football Predictor
                  </h1>
                  <p className="text-xl text-gray-600 mb-8">
                    Machine Learning Sports Predictions
                  </p>
                  <p className="text-gray-500">
                    Pages are under development. Check back soon!
                  </p>
                </div>
              } 
            />
            
            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  )
}

export default App
