import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

type User = {
  id: number;
  username: string;
  email: string;
  is_email_verified: boolean;
};

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (params: { username: string; password: string }) => Promise<void>;
  register: (params: { username: string; email: string; password: string; password_confirm: string }) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<boolean>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  useEffect(() => {
    const bootstrap = async () => {
      try {
        // If we have an access token, try to fetch profile
        if (api.getAccessToken()) {
          const me = await api.getProfile<User>();
          setUser(me);
        }
      } catch {
        // Attempt refresh via cookie
        try {
          const refreshed = await api.refreshAccessToken();
          if (refreshed) {
            const me = await api.getProfile<User>();
            setUser(me);
          } else {
            setUser(null);
          }
        } catch {
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    };
    bootstrap();
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login: async ({ username, password }) => {
      await api.login(username, password);
      const me = await api.getProfile<User>();
      setUser(me);
    },
    register: async ({ username, email, password, password_confirm }) => {
      await api.register({ username, email, password, password_confirm });
    },
    logout: async () => {
      await api.logout();
      // Clear all cached queries to avoid showing stale authenticated data
      try { queryClient.clear(); } catch { /* no-op */ }
      setUser(null);
      navigate('/login', { replace: true });
    },
    refresh: async () => {
      const refreshed = await api.refreshAccessToken();
      if (refreshed) {
        try {
          const me = await api.getProfile<User>();
          setUser(me);
        } catch {
          setUser(null);
          return false;
        }
      }
      return refreshed;
    }
  }), [user, isLoading]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};



