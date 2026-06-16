"use client";
/**
 * Auth Context
 * Provides user state and auth actions throughout the app.
 * Wrap your layout with <AuthProvider>.
 */
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";
import type { User, LoginPayload, RegisterPayload } from "@/types";
import { authService } from "@/services/auth.service";
import { getAccessToken } from "@/services/api";
import toast from "react-hot-toast";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Fetch current user on mount (if token exists)
  const refreshUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const me = await authService.getMe();
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (payload: LoginPayload) => {
    await authService.login(payload);
    const me = await authService.getMe();
    setUser(me);
    toast.success(`Welcome back, ${me.full_name.split(" ")[0]}! 👋`);
    router.push("/dashboard");
  };

  const register = async (payload: RegisterPayload) => {
    await authService.register(payload);
    // Auto-login after register
    await authService.login({ email: payload.email, password: payload.password });
    const me = await authService.getMe();
    setUser(me);
    toast.success("Account created successfully! 🎉");
    router.push("/dashboard");
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    toast.success("Logged out successfully");
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within <AuthProvider>");
  return context;
}
