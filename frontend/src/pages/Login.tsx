import { useState, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const form = new FormData();
      form.append('email', email);
      form.append('password', password);
      const res = await fetch('/login', { method: 'POST', body: form });
      if (res.ok) {
        window.location.href = '/app';
      } else {
        setError('Login failed');
      }
    } catch {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white p-8 rounded-2xl border shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">Sign in</h1>
        <p className="text-gray-500 text-sm mb-6">Access your dashboard.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required className="mt-1.5"/>
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required className="mt-1.5"/>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>{loading? 'Signing in...':'Sign in'}</Button>
          <p className="text-center text-sm text-gray-600">No account? <a href="/app/register" className="text-blue-600 hover:underline">Create one</a></p>
          {error && <div className="p-3 rounded-lg bg-red-100 border border-red-200 text-red-700 text-sm">{error}</div>}
        </form>
      </div>
    </div>
  );
}
