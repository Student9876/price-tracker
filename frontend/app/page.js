import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-50">
      <div className="text-center">
        <h1 className="text-5xl font-extrabold text-slate-800">
          Welcome to Price<span className="text-indigo-600">Track</span>
        </h1>
        <p className="mt-4 text-lg text-slate-600">
          Never miss a deal again. We watch the prices so you don&apos;t have to.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link href="/login" className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition">
              Login
          </Link>
          <Link href="/dashboard" className="px-6 py-3 bg-white text-slate-700 font-semibold rounded-lg shadow-md hover:bg-slate-100 transition">
              Go to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}