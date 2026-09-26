"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { useAuthStore } from "@/store/auth";
import type { UserRole } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error } = useAuthStore();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("patient");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await register(email, password, fullName, role);
      router.push("/login");
    } catch {
      // error already captured in the store and shown below
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4 dark:bg-brand-900">
      <div className="fixed right-4 top-4">
        <ThemeToggle />
      </div>
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold text-brand-600 dark:text-brand-100">Create your account</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Join MediTwin AI</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
          <Input label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required autoFocus />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required />

          <div className="flex flex-col gap-1.5">
            <label htmlFor="role" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              I am a
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-900 outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-brand-900/40 dark:text-gray-100"
            >
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
              <option value="nurse">Nurse</option>
              <option value="reception">Reception</option>
            </select>
          </div>

          {error && <p className="text-sm text-red-600 dark:text-red-400" role="alert">{error}</p>}

          <Button type="submit" isLoading={isLoading} className="mt-2 w-full">
            Create account
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-brand-500 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
