import React from 'react'

export default function ProgramTable({ data }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white shadow rounded-lg overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left text-sm font-medium">Manobra</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Punto</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Descripción</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Fase</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Código</th>
            <th className="px-4 py-2 text-left text-sm font-medium">Subcódigo</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={idx}
              className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
            >
              <td className="px-4 py-2 text-sm">{row.manobra_normalizada}</td>
              <td className="px-4 py-2 text-sm">{row.punto_programa}</td>
              <td className="px-4 py-2 text-sm whitespace-normal">{row.descripcion}</td>
              <td className="px-4 py-2 text-sm">{row.activity_phase}</td>
              <td className="px-4 py-2 text-sm">{row.activity_code}</td>
              <td className="px-4 py-2 text-sm">{row.activity_subcode}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
