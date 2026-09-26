"use client";

import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { useAuthStore } from "@/store/auth";
import type { UserRole } from "@/lib/api";

const ROLE_HOME: Record<UserRole, string> = {
  patient: "/patient", doctor: "/doctor", nurse: "/nurse", reception: "/reception", admin: "/admin",
};

interface DashboardShellProps {
  allowedRoles: UserRole[];
  title: string;
  children: ReactNode;
}

export function DashboardShell({ allowedRoles, title, children }: DashboardShellProps) {
  const router = useRouter();
  const { user, hydrate, logout } = useAuthStore();

  useEffect(() => {
    (async () => {
      await hydrate();
      const current = useAuthStore.getState().user;
      if (!current) {
        router.replace("/login");
      } else if (!allowedRoles.includes(current.role)) {
        // Logged in but wrong role for this dashboard — send to their own
        router.replace(ROLE_HOME[current.role] ?? "/login");
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-brand-900">
        <p className="text-sm text-gray-500 dark:text-gray-400">Checking your session…</p>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-brand-900">
      <aside className="flex w-60 flex-col justify-between border-r border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-brand-900/60">
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-lg font-semibold text-brand-600 dark:text-brand-100">MediTwin AI</h1>
              <p className="mt-1 text-xs text-gray-400">Predict. Prevent. Protect.</p>
            </div>
            <ThemeToggle />
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <p className="truncate text-sm font-medium text-gray-700 dark:text-gray-200">{user.full_name}</p>
          <p className="text-xs capitalize text-gray-400">{user.role}</p>
          <Button
            variant="ghost"
            className="mt-2"
            onClick={() => {
              logout();
              router.replace("/login");
            }}
          >
            Log out
          </Button>
        </div>
      </aside>

      <main className="flex-1 p-8">
        <h2 className="mb-6 text-xl font-semibold text-gray-900 dark:text-gray-100">{title}</h2>
        {children}
      </main>
    </div>
  );
}
