"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#020617] text-slate-50 p-8 text-center">
      <h1 className="text-4xl font-bold mb-4 text-red-500">
        Systemic Anomaly Detected
      </h1>
      <p className="text-slate-400 max-w-md">
        An unexpected error occurred within the causal trace engine.
        {error.message && (
          <span className="block mt-2 text-red-400/60 font-mono text-xs">
            {error.message}
          </span>
        )}
      </p>
      <button
        onClick={() => reset()}
        className="mt-8 px-6 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700"
      >
        Attempt Re-initialization
      </button>
    </div>
  );
}
