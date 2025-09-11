import clsx from 'clsx';

const colors: Record<string, string> = {
  PASS: 'bg-green-600',
  FAIL: 'bg-red-600',
  WAIVED: 'bg-blue-600',
  NA: 'bg-gray-600'
};

export function StatusBadge({ status }: { status: keyof typeof colors }) {
  return (
    <span className={clsx('px-2 py-1 rounded text-white text-xs', colors[status])}>
      {status}
    </span>
  );
}
