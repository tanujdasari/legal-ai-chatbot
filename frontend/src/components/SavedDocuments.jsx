
import { useEffect, useState } from "react";
import {
  FileText,
  Trash2,
  RefreshCw,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function SavedDocuments({
  conversationId,
  onSelectDocument,
  onDocumentDeleted,
  selectedDocumentId = null,
  refreshKey = 0,
  disabled = false,
}) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDocuments() {
      if (!conversationId) {
        setDocuments([]);
        return;
      }

      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          `${API_URL}/api/documents`
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load saved documents."
          );
        }

        const data = await response.json();

        if (!cancelled) {
          setDocuments(
            data.filter(
              (doc) =>
                doc.conversation_id === conversationId
            )
          );
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Unable to load documents."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDocuments();

    return () => {
      cancelled = true;
    };
  }, [conversationId, refreshKey]);

  async function handleDelete(doc) {
    if (disabled || deletingId) return;

    const confirmed = window.confirm(
      `Permanently delete "${doc.filename}"?\n\n` +
      "The uploaded PDF and its saved record will be removed."
    );

    if (!confirmed) return;

    setDeletingId(doc.document_id);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/documents/${encodeURIComponent(
          doc.document_id
        )}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Unable to delete PDF (${response.status}).`
        );
      }

      setDocuments((previous) =>
        previous.filter(
          (item) =>
            item.document_id !== doc.document_id
        )
      );

      onDocumentDeleted?.(doc.document_id);
    } catch (err) {
      setError(
        err.message || "Unable to delete document."
      );
    } finally {
      setDeletingId(null);
    }
  }

  if (!conversationId) {
    return null;
  }

  return (
    <section className="saved-documents">
      <h3>Saved Legal Documents</h3>

      {loading && (
        <p>Loading saved documents...</p>
      )}

      {error && (
        <p role="alert">{error}</p>
      )}

      {!loading && !error && documents.length === 0 && (
        <p>No PDFs associated with this conversation.</p>
      )}

      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className={`saved-document-item ${
  selectedDocumentId === doc.document_id
    ? "saved-document-active"
    : ""
}`}
        >
          <button
            type="button"
            disabled={disabled || deletingId !== null}
            onClick={() =>
  onSelectDocument(doc.document_id, doc.filename)
}
            className="saved-document-select"
            title="Use this PDF for legal questions"
          >
            <FileText size={18} />
            <span>{doc.filename}</span>
            <span>{doc.jurisdiction}</span>
          </button>

          <button
            type="button"
            disabled={disabled || deletingId !== null}
            onClick={() => handleDelete(doc)}
            className="saved-document-delete"
            title={`Delete ${doc.filename}`}
            aria-label={`Delete ${doc.filename}`}
          >
            {deletingId === doc.document_id ? (
              <RefreshCw size={17} />
            ) : (
              <Trash2 size={17} />
            )}
          </button>
        </div>
      ))}
    </section>
  );
}
