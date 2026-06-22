import api from "./api";

export const intelligenceService = {
  // -- Sessions --------------------------------------------------------------
  async listSessions() {
    const { data } = await api.get(`/automl/sessions`);
    return data;
  },
  async getBestSession(datasetId: number) {
    const { data } = await api.get(`/automl/best-session/${datasetId}`);
    return data;
  },

  // -- Data Quality ------------------------------------------------------------
  async getQualityReport(datasetId: number) {
    const { data } = await api.get(`/data-quality/report/${datasetId}`);
    return data;
  },
  async getQualityScore(datasetId: number) {
    const { data } = await api.get(`/data-quality/score/${datasetId}`);
    return data;
  },
  async getCorrelation(datasetId: number) {
    const { data } = await api.get(`/data-quality/correlation/${datasetId}`);
    return data;
  },
  async getMissingValues(datasetId: number) {
    const { data } = await api.get(`/data-quality/missing/${datasetId}`);
    return data;
  },

  // -- Explainability (SHAP) ----------------------------------------------------
  async explainModel(sessionId: string, numSamples: number = 100) {
    const { data } = await api.post(`/explainability/explain`, {
      session_id: sessionId,
      num_samples: numSamples,
    });
    return data;
  },
  async getFeatureImportance(sessionId: string, numSamples: number = 100) {
    const { data } = await api.post(`/explainability/feature-importance`, {
      session_id: sessionId,
      num_samples: numSamples,
    });
    return data;
  },

  // -- AI Chat Assistant --------------------------------------------------------
  async sendChatMessage(datasetId: number, message: string, sessionId?: string) {
    const { data } = await api.post(`/chat/message`, {
      dataset_id: datasetId,
      message,
      session_id: sessionId,
    });
    return data;
  },
  async getQuickInsights(datasetId: number) {
    const { data } = await api.get(`/chat/insights/${datasetId}`);
    return data;
  },
  async getChatHistory(datasetId: number) {
    const { data } = await api.get(`/chat/history/${datasetId}`);
    return data;
  },
  async resetChat(datasetId: number) {
    const { data } = await api.post(`/chat/reset`, { dataset_id: datasetId });
    return data;
  },

  // -- Reports ------------------------------------------------------------------
  async generatePdfReport(datasetId: number, modelName?: string) {
    const { data } = await api.post(`/reports/generate-pdf`, {
      dataset_id: datasetId,
      model_name: modelName,
      include_shap: !!modelName,
    });
    return data;
  },
  async exportExcelReport(datasetId: number, modelName?: string) {
    const { data } = await api.post(`/reports/export-excel`, {
      dataset_id: datasetId,
      model_name: modelName,
      include_shap: !!modelName,
    });
    return data;
  },
  async listReports() {
    const { data } = await api.get(`/reports/list`);
    return data;
  },

  async predictFromForm(sessionId: string, rawData: Record<string, any>) {
    const { data } = await api.post(`/automl/predict-from-form/${sessionId}`, { raw_data: rawData });
    return data;
  },
async downloadReport(filename: string) {
    const response = await api.get(`/reports/download/${filename}`, {
      responseType: "blob",
    });
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};