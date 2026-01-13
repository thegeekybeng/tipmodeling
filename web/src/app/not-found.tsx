export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#020617] text-slate-50">
      <h1 className="text-4xl font-bold mb-4">404 - Strategic Data Missing</h1>
      <p className="text-slate-400">
        The requested intelligence node could not be located.
      </p>
      <a
        href="/"
        className="mt-8 px-6 py-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
      >
        Return to Mission Control
      </a>
    </div>
  );
}
