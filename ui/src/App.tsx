import JobList from "./components/JobList";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">CS / Quant Job Dashboard</h1>
          <p className="text-gray-500">Software, data, and quant roles — updated from public boards.</p>
        </header>
        <JobList />
      </div>
    </div>
  );
}
