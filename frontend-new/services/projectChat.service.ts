import api from "./api";

export const projectChatService = {
  async sendMessage(message: string) {
    const { data } = await api.post(`/project-chat/message`, { message });
    return data;
  },
  async getHistory() {
    const { data } = await api.get(`/project-chat/history`);
    return data;
  },
  async resetChat() {
    const { data } = await api.post(`/project-chat/reset`);
    return data;
  },
};
