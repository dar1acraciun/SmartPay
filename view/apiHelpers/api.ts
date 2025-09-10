import axios from "axios";

export interface UploadResponse {
  message: string;
  file_id: string;
  path: string;
  brand: string;
  downgraded_transaction: number;
}

const API_BASE = "http://localhost:8000";

/**
 * Upload a CSV file to FastAPI.
 * Returns the parsed server response if successful.
 * Throws if status >= 400.
 */
export async function uploadTransactionFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await axios.post<UploadResponse>(`${API_BASE}/files/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err: any) {
    // Axios wraps errors; prefer server error detail if available
    const detail = err.response?.data?.detail || err.message || "Upload failed";
    throw new Error(detail);
  }
}
