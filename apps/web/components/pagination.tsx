'use client';
import { useRouter, useSearchParams } from 'next/navigation';

export function Pagination({ page, total }: { page: number; total: number }) {
  const router = useRouter();
  const params = useSearchParams();
  function go(p: number) {
    const qp = new URLSearchParams(params);
    qp.set('page', String(p));
    router.push(`?${qp.toString()}`);
  }
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => go(page - 1)}
        disabled={page <= 1}
        className="px-2 py-1 border rounded"
      >
        Prev
      </button>
      <span>{page}</span>
      <button
        onClick={() => go(page + 1)}
        disabled={page >= total}
        className="px-2 py-1 border rounded"
      >
        Next
      </button>
    </div>
  );
}
