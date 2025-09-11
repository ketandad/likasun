import { ReactNode } from 'react';

interface Column<T> {
  key: keyof T;
  header: ReactNode;
  render?: (row: T) => ReactNode;
}
interface Props<T> {
  columns: Column<T>[];
  data: T[];
}

export function DataTable<T extends { id?: string | number }>({ columns, data }: Props<T>) {
  return (
    <table className="min-w-full text-sm">
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={String(col.key)} className="p-2 text-left">
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={row.id ?? i} className="border-t border-gray-700">
            {columns.map((col) => (
              <td key={String(col.key)} className="p-2">
                {col.render ? col.render(row) : String(row[col.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
