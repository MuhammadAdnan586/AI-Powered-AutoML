import api from "./api";

export interface PreprocessingConfig {
  dataset_id: number;
  target_column: string;
  remove_duplicates?: boolean;
  missing_strategy?: string;
  encoding_strategy?: string;
  scaling_method?: string;
  drop_threshold?: number;
}

export interface FeatureEngineeringConfig {
  processed_dataset_id: number;
  target_column: string;
  problem_type?: string;
  auto_generate?: boolean;
  remove_low_variance?: boolean;
  remove_correlated?: boolean;
  select_best?: boolean;
  k_best?: number;
}

export interface TrainingConfig {
  engineered_dataset_id: number;
  target_column: string;
  problem_type: string;
  test_size?: number;
  models_to_train?: string[] | null;
  hyperparameter_tuning?: boolean;
}

export interface LeaderboardEntry {
  model_name: string;
  display_name?: string;
  score: number;
  metric?: string;
  [key: string]: any;
}

export const automlService = {
  // -- Preprocessing --------------------------------------------------------
  async analyzeDataset(datasetId: number) {
    const { data } = await api.post(`/preprocessing/analyze?dataset_id=${datasetId}`);
    return data;
  },

  async detectProblemType(datasetId: number, targetColumn: string) {
    const { data } = await api.post(`/preprocessing/detect-problem-type`, {
      dataset_id: datasetId,
      target_column: targetColumn,
    });
    return data;
  },

  async runPreprocessing(config: PreprocessingConfig) {
    const { data } = await api.post(`/preprocessing/run`, config);
    return data;
  },

  // -- Feature Engineering --------------------------------------------------
  async runFeatureEngineering(config: FeatureEngineeringConfig) {
    const { data } = await api.post(`/feature-engineering/run`, config);
    return data;
  },

  async getCorrelationMatrix(processedDatasetId: number) {
    const { data } = await api.get(`/feature-engineering/correlation/${processedDatasetId}`);
    return data;
  },

  // -- AutoML Training ------------------------------------------------------
  async startTraining(config: TrainingConfig) {
    const { data } = await api.post(`/automl/train`, config);
    return data;
  },

  async getTrainingStatus(sessionId: string) {
    const { data } = await api.get(`/automl/status/${sessionId}`);
    return data;
  },

  async getLeaderboard(sessionId: string) {
    const { data } = await api.get(`/automl/leaderboard/${sessionId}`);
    return data;
  },

async listSessions(datasetId?: number) {
    const url = datasetId
        ? `/automl/sessions?dataset_id=${datasetId}`
        : `/automl/sessions`;
    const { data } = await api.get(url);
    return data;
},

  async getFullReport(sessionId: string) {
    // Use status endpoint which returns full results
    const { data } = await api.get(`/automl/status/${sessionId}`);
    const results = data.results ?? {};
    return {
      ...results,
      session_id: sessionId,
      status: data.status,
    };
  },
async getProcessedPreview(processedDatasetId: number, rows: number = 10) {
    const { data } = await api.get(`/preprocessing/preview/${processedDatasetId}?rows=${rows}`);
    return data;
  },

  async getEngineeredPreview(engineeredDatasetId: number, rows: number = 10) {
    const { data } = await api.get(`/feature-engineering/preview/${engineeredDatasetId}?rows=${rows}`);
    return data;
  },
  async listAvailableModels(problemType: string = "classification") {
    const { data } = await api.get(`/automl/models?problem_type=${problemType}`);
    return data;
  },
// -- Downloads -------------------------------------------------------------
  async downloadTrainedModel(sessionId: string) {
    const response = await api.get(`/automl/download-model/${sessionId}`, {
      responseType: "blob",
    });
    const disposition = response.headers["content-disposition"];
    let filename = `model_${sessionId}.pkl`;
    if (disposition) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match) filename = match[1];
    }
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
  async downloadEngineeredDataset(sessionId: string) {
    const response = await api.get(`/automl/download-dataset/${sessionId}`, {
      responseType: "blob",
    });
    const disposition = response.headers["content-disposition"];
    let filename = `engineered_dataset_${sessionId}.csv`;
    if (disposition) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match) filename = match[1];
    }
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
