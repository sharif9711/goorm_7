import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
    }),
    { name: 'auth-storage' }
  )
);

interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: true,
      toggleTheme: () => set((s) => ({ isDark: !s.isDark })),
    }),
    { name: 'theme-storage' }
  )
);

interface AnalysisState {
  currentResult: import('@/types').AnalysisResult | null;
  setResult: (result: import('@/types').AnalysisResult | null) => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentResult: null,
  setResult: (result) => set({ currentResult: result }),
}));
