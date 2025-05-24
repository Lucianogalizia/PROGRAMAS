// frontend/src/api/pullingApi.js

import axios from 'axios'

// Base URL según entorno (define VITE_API_URL en .env para producción)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

/**
 * Sube el Excel y recibe el JSON con el programa de maniobras.
 * @param {File} file – objeto File del input
 * @returns {Promise<Array>} – array de maniobras
 */
export async function generateProgram(file) {
  const formData = new FormData()
  formData.append('file', file)

  const resp = await api.post('/process/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return resp.data.program
}
