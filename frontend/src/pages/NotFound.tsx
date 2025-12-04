export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="mb-4 text-4xl font-bold">404</h1>
        <p className="mb-4 text-xl text-gray-500">Oops! Page not found</p>
        <a href="/app" className="text-blue-600 underline hover:text-blue-700">Return to Dashboard</a>
      </div>
    </div>
  );
}
