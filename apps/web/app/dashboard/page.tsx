export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl mb-4">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-800 p-4 rounded">PASS</div>
        <div className="bg-gray-800 p-4 rounded">FAIL</div>
        <div className="bg-gray-800 p-4 rounded">WAIVED</div>
      </div>
    </div>
  );
}
