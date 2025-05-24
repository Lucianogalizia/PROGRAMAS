// frontend/src/components/UploadForm.jsx

import React, { useState } from 'react'
import { generateProgram } from '../api/pullingApi'
import ProgramTable from './ProgramTable'

export default function UploadForm() {
  const [file, setFile] = useState(null)
  const [program, setProgram] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Por favor selecciona un archivo Excel.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await generateProgram(file)
      setProgram(result)
    } catch (err) {
      console.error(err)
      setError(
        err.response?.data?.detail ||
        'Error al generar el programa. Intenta de nuevo.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-lg mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="file"
          accept=".xls,.xlsx,.xlsm"
          onChange={handleFileChange}
          className="border rounded px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 text-white rounded px-4 py-2 hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Generando…' : 'Generar Programa'}
        </button>
      </form>

      {error && (
        <p className="mt-4 text-red-600 text-center">
          {error}
        </p>
      )}

      {program.length > 0 && (
        <div className="mt-8">
          <ProgramTable data={program} />
        </div>
      )}
    </div>
)
}
