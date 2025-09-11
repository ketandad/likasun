'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '../../lib/api';
import { useToast } from '../../components/toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const { push } = useToast();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post('/auth/login', { email, password });
      router.push('/dashboard');
    } catch {
      push('Login failed');
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <form onSubmit={submit} className="flex flex-col gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="p-2 rounded bg-gray-800 text-white"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="p-2 rounded bg-gray-800 text-white"
        />
        <button type="submit" className="bg-blue-600 text-white p-2 rounded">
          Login
        </button>
      </form>
    </div>
  );
}
