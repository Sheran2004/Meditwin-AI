"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { useAuthStore } from "@/store/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const user = await login(email, password);
      const roleRoutes: Record<string, string> = {
        doctor: "/doctor", admin: "/admin", nurse: "/nurse", reception: "/reception", patient: "/patient",
      };
      router.push(roleRoutes[user.role] ?? "/doctor");
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
          <h1 className="text-2xl font-semibold text-brand-600 dark:text-brand-100">MediTwin AI</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Predict. Prevent. Protect.</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

          {error && <p className="text-sm text-red-600 dark:text-red-400" role="alert">{error}</p>}

          <Button type="submit" isLoading={isLoading} className="mt-2 w-full">
            Sign in
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          New here?{" "}
          <Link href="/register" className="font-medium text-brand-500 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}
