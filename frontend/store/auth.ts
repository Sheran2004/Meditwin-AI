/**
 * Client-side auth state. Access/refresh tokens live in localStorage
 * (read by the axios interceptor in lib/api.ts); this store just holds
 * the current user object and loading/error state for the UI.
 */
import { create } from "zustand";
import { fetchMe, login as apiLogin, register as apiRegister, type User, type UserRole } from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<User>;
  register: (email: string, password: string, fullName: string, role: UserRole) => Promise<User>;
  logout: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await apiLogin(email, password);
      localStorage.setItem("meditwin_access_token", tokens.access_token);
      localStorage.setItem("meditwin_refresh_token", tokens.refresh_token);
      const user = await fetchMe();
      set({ user, isLoading: false });
      return user;
    } catch (err: any) {
      const message = err?.response?.data?.detail ?? "Login failed. Please try again.";
      set({ isLoading: false, error: message });
      throw new Error(message);
    }
  },

  register: async (email, password, fullName, role) => {
    set({ isLoading: true, error: null });
    try {
      const user = await apiRegister(email, password, fullName, role);
      set({ isLoading: false });
      return user;
    } catch (err: any) {
      const message = err?.response?.data?.detail ?? "Registration failed. Please try again.";
      set({ isLoading: false, error: message });
      throw new Error(message);
    }
  },

  logout: () => {
    localStorage.removeItem("meditwin_access_token");
    localStorage.removeItem("meditwin_refresh_token");
    set({ user: null });
  },

  hydrate: async () => {
    const token = localStorage.getItem("meditwin_access_token");
    if (!token) return;
    try {
      const user = await fetchMe();
      set({ user });
    } catch {
      localStorage.removeItem("meditwin_access_token");
      localStorage.removeItem("meditwin_refresh_token");
    }
  },
}));
