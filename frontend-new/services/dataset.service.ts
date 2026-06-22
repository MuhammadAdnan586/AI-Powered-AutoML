import api from "./api";
import type { Dataset, DatasetListItem, DatasetVersion } from "@/types";

export const datasetService = {
  async upload(
    file: File,
    name: string,
    description?: string
  ): Promise<Dataset> {
    const form = new FormData();
    form.append("file", file);
    form.append("name", name);
    if (description) form.append("description", description);

    const { data } = await api.post<Dataset>("/datasets/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async list(skip = 0, limit = 20): Promise<DatasetListItem[]> {
    const { data } = await api.get<DatasetListItem[]>("/datasets/", {
      params: { skip, limit },
    });
    return data;
  },

  async getById(id: number): Promise<Dataset> {
    const { data } = await api.get<Dataset>(`/datasets/${id}`);
    return data;
  },

  async update(
    id: number,
    payload: { name?: string; description?: string }
  ): Promise<Dataset> {
    const { data } = await api.put<Dataset>(`/datasets/${id}`, payload);
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/datasets/${id}`);
  },

  async createVersion(
    datasetId: number,
    file: File,
    versionLabel?: string,
    notes?: string
  ): Promise<DatasetVersion> {
    const form = new FormData();
    form.append("file", file);
    if (versionLabel) form.append("version_label", versionLabel);
    if (notes) form.append("notes", notes);

    const { data } = await api.post<DatasetVersion>(
      `/datasets/${datasetId}/versions`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return data;
  },

  async getVersions(datasetId: number): Promise<DatasetVersion[]> {
    const { data } = await api.get<DatasetVersion[]>(
      `/datasets/${datasetId}/versions`
    );
    return data;
  },

  getDownloadUrl(datasetId: number, version?: number): string {
    const base = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/datasets/${datasetId}/download`;
    return version ? `${base}?version=${version}` : base;
  },
};
