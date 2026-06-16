import api, { setTokens, clearTokens, getRefreshToken } from "./api";
import type {
  LoginPayload,
  RegisterPayload,
  AuthTokens,
  User,
} from "@/types";

export const authService = {
  async register(payload: RegisterPayload): Promise<User> {
    const { data } = await api.post<User>("/auth/register", payload);
    return data;
  },

  async login(payload: LoginPayload): Promise<AuthTokens> {
    const { data } = await api.post<AuthTokens>("/auth/login", payload);
    setTokens(data.access_token, data.refresh_token);
    return data;
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },

  async logout(): Promise<void> {
    const refresh_token = getRefreshToken();
    if (refresh_token) {
      try {
        await api.post("/auth/logout", { refresh_token });
      } catch (_) {}
    }
    clearTokens();
  },

  async changePassword(currentPassword: string, newPassword: string) {
    const { data } = await api.put("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return data;
  },
};
