import { useState, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [alerts, setAlerts] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (password !== confirm) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      const form = new FormData();
      form.append('name', name);
      form.append('email', email);
      form.append('password', password);
      form.append('confirm_password', confirm);
      form.append('receive_alerts', alerts ? 'on' : 'off');
      const res = await fetch('/register', { method: 'POST', body: form });
      if (res.ok) {
        window.location.href = '/app/login';
      } else {
        setError('Registration failed');
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
        <h1 className="text-2xl font-semibold mb-2">Create account</h1>
        <p className="text-gray-500 text-sm mb-6">Join Smart Traffic Monitoring.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={name} onChange={e=>setName(e.target.value)} required className="mt-1.5"/>
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required className="mt-1.5"/>
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required className="mt-1.5"/>
          </div>
          <div>
            <Label htmlFor="confirm">Confirm Password</Label>
            <Input id="confirm" type="password" value={confirm} onChange={e=>setConfirm(e.target.value)} required className="mt-1.5"/>
          </div>
          <div className="flex items-center gap-2">
            <Checkbox id="alerts" checked={alerts} onCheckedChange={(v)=>setAlerts(!!v)} />
            <Label htmlFor="alerts" className="text-sm font-normal cursor-pointer">Receive email alerts</Label>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>{loading? 'Creating account...':'Create account'}</Button>
          <p className="text-center text-sm text-gray-600">Already have an account? <a href="/app/login" className="text-blue-600 hover:underline">Sign in</a></p>
          {error && <div className="p-3 rounded-lg bg-red-100 border border-red-200 text-red-700 text-sm">{error}</div>}
        </form>
      </div>
    </div>
  );
}
