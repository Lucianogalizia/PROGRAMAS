import React from 'react'
import UploadForm from './components/UploadForm.jsx'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col items-center p-4">
      <h1 className="text-3xl font-bold mb-6">Generador de Programas de Pulling</h1>
      <UploadForm />
    </div>
  )
}
