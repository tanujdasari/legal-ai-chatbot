import { useState } from "react";
import { FileUp, CheckCircle2, AlertCircle } from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

export default function DocumentUpload({
  jurisdiction,
  onUploaded,
  disabled = false,
}) {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  async function handleUpload(event) {
    const file = event.target.files?.[0];

    if (!file || disabled || uploading) return;

    setMessage("");
    setError(false);

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setMessage("Please select a PDF file.");
      setError(true);
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setMessage("PDF must be 10 MB or smaller.");
      setError(true);
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("jurisdiction", jurisdiction);

    setUploading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to upload PDF."
        );
      }

      onUploaded(data.document_id);

      setMessage(
        `${data.filename} uploaded successfully (${data.chunks} chunks).`
      );
    } catch (err) {
      setError(true);
      setMessage(err.message || "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="document-upload">
      <label
        htmlFor="legal-pdf"
        style={{
          opacity: disabled || uploading ? 0.5 : 1,
          cursor: disabled || uploading ? "not-allowed" : "pointer",
        }}
      >
        <FileUp size={18} />
        {uploading ? "Processing PDF..." : "Upload Legal PDF"}
      </label>

      <input
        id="legal-pdf"
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleUpload}
        disabled={disabled || uploading}
      />

      {message && (
        <p
          className={
            error
              ? "upload-message error"
              : "upload-message success"
          }
          role="status"
        >
          {error ? (
            <AlertCircle size={15} />
          ) : (
            <CheckCircle2 size={15} />
          )}
          {message}
        </p>
      )}
    </div>
  );
}