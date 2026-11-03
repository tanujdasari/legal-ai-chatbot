
import { useEffect, useRef, useState } from "react";
import { Scale } from "lucide-react";

import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import DocumentUpload from "./components/DocumentUpload";
import SavedDocuments from "./components/SavedDocuments";

import { sendLegalQuestion } from "./services/api";
import {
  getConversations,
  createConversation,
  getConversation,
  saveMessage,
  deleteConversation,
} from "./services/historyApi";

import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function documentRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === "string" ? data.detail : `Document API error (${response.status})`);
  }
  return response.json();
}

async function getConversationDocument(conversationId) {
  const documents = await documentRequest("/api/documents");
  return documents.find((doc) => doc.conversation_id === conversationId) || null;
}

async function attachDocument(documentId, conversationId) {
  return documentRequest(`/api/documents/${encodeURIComponent(documentId)}/conversation`, {
    method: "PATCH",
    body: JSON.stringify({ conversation_id: conversationId }),
  });
}


const categories = [
  "immigration",
  "criminal",
  "civil",
  "family",
  "employment",
  "property",
  "business",
  "contracts",
  "other",
];

function parseSources(value) {
  if (!value) return [];

  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] =
    useState(null);

  const [jurisdiction, setJurisdiction] = useState("US");
  const [category, setCategory] = useState("immigration");
  const [state, setState] = useState("");

  const [documentId, setDocumentId] = useState(null);
  const [documentVersion, setDocumentVersion] = useState(0);
  const [documentsRefreshKey, setDocumentsRefreshKey] = useState(0);
  const [activeDocumentName, setActiveDocumentName] = useState("");

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  const busyRef = useRef(false);

  async function refreshConversations() {
    const data = await getConversations();
    setConversations(data);
  }

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        const data = await getConversations();

        if (!cancelled) {
          setConversations(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "Unable to load chat history."
          );
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSend(question) {
    if (busyRef.current || historyLoading) return;

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) return;

    busyRef.current = true;
    setLoading(true);
    setError("");

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);

    let conversationId = activeConversationId;

    try {
      if (!conversationId) {
        const conversation = await createConversation({
          title: trimmedQuestion.slice(0, 80),
          jurisdiction,
          category,
          state: state.trim() || null,
        });

        conversationId = conversation.id;
        setActiveConversationId(conversationId);

        if (documentId) {
          await attachDocument(documentId, conversationId);
        }
        await refreshConversations();
      }

      await saveMessage(conversationId, {
        role: "user",
        content: trimmedQuestion,
      });

      const result = await sendLegalQuestion({
        question: trimmedQuestion,
        jurisdiction,
        category,
        state: state.trim() || null,
        document_id: documentId,
      });

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: result.answer,
        disclaimer: result.disclaimer,
        sources: result.sources || [],
      };

      await saveMessage(conversationId, {
        role: "assistant",
        content: result.answer,
        disclaimer: result.disclaimer || null,
        sources: JSON.stringify(result.sources || []),
      });

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

      await refreshConversations();
    } catch (err) {
      setError(
        err.message || "Unable to save or process the chat."
      );
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  function handleNewChat() {
    if (busyRef.current || historyLoading) return;

    setActiveConversationId(null);
    setMessages([]);
    setDocumentId(null);
    setDocumentVersion((previous) => previous + 1);
    setError("");
    setActiveDocumentName("");
  }

  async function handleSelectConversation(conversationId) {
    if (busyRef.current || historyLoading) return;

    busyRef.current = true;
    setLoading(true);
    setError("");

    try {
      const conversation = await getConversation(conversationId);
      const savedDocument = await getConversationDocument(conversationId);

      setActiveConversationId(conversation.id);
      setJurisdiction(conversation.jurisdiction);
      setCategory(conversation.category);
      setState(conversation.state || "");

      setDocumentId(savedDocument?.document_id || null);
      setActiveDocumentName(savedDocument?.filename || "");
      setDocumentVersion((previous) => previous + 1);

      setMessages(
        conversation.messages.map((message) => ({
          id: message.id,
          role: message.role,
          content: message.content,
          disclaimer: message.disclaimer,
          sources: parseSources(message.sources),
        }))
      );
    } catch (err) {
      setError(
        err.message || "Unable to open conversation."
      );
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  async function handleDeleteConversation(conversationId) {
    if (busyRef.current || historyLoading) return;

    busyRef.current = true;
    setLoading(true);
    setError("");

    try {
      await deleteConversation(conversationId);

      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
        setMessages([]);
        setDocumentId(null);
        setDocumentVersion((previous) => previous + 1);
      }

      await refreshConversations();
    } catch (err) {
      setError(
        err.message || "Unable to delete conversation."
      );
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  function handleJurisdictionChange(event) {
    if (busyRef.current || historyLoading) return;

    setJurisdiction(event.target.value);
    setState("");
    setDocumentId(null);
    setDocumentVersion((previous) => previous + 1);

    setActiveConversationId(null);
    setMessages([]);
    setError("");
  }

  function handleCategoryChange(event) {
    if (busyRef.current || historyLoading) return;

    setCategory(event.target.value);

    // Start a new conversation when changing categories.
    setActiveConversationId(null);
    setMessages([]);
    setDocumentId(null);
    setDocumentVersion((previous) => previous + 1);
    setError("");
  }

  async function handleDocumentUploaded(id) {
    if (busyRef.current || historyLoading) return;

    busyRef.current = true;
    setLoading(true);
    setError("");

    try {
      let conversationId = activeConversationId;
      if (!conversationId) {
        const conversation = await createConversation({
          title: "PDF legal consultation",
          jurisdiction,
          category,
          state: state.trim() || null,
        });
        conversationId = conversation.id;
        setActiveConversationId(conversationId);
      }
      await attachDocument(id, conversationId);
      setDocumentId(id);
      const documentInfo = await documentRequest(
  `/api/documents/${encodeURIComponent(id)}`
);

setActiveDocumentName(documentInfo.filename || "");
      setDocumentsRefreshKey((previous) => previous + 1);
      await refreshConversations();
    } catch (err) {
      setError(err.message || "Unable to link PDF to conversation.");
      // Do not set documentId until its association has succeeded.
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  function handleRemoveDocument() {
    if (busyRef.current) return;
    setDocumentId(null);
    setActiveDocumentName("");
    setDocumentVersion((previous) => previous + 1);
    setError("");
  }

  return (
    <div className="app-layout">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        loading={loading || historyLoading}
      />

      <main className="main-panel">
        <header className="topbar">
          <div className="topbar-title">
            <Scale size={23} />
            <div>
              <h1>Legal AI Assistant</h1>
              <p>Legal information for the US and India</p>
            </div>
          </div>

          <span className="status-badge">
            AI Assistant
          </span>
        </header>

        <section className="controls">
          <label>
            Jurisdiction
            <select
              value={jurisdiction}
              disabled={loading || historyLoading}
              onChange={handleJurisdictionChange}
            >
              <option value="US">United States</option>
              <option value="IN">India</option>
            </select>
          </label>

          <label>
            Legal Category
            <select
              value={category}
              disabled={loading || historyLoading}
              onChange={handleCategoryChange}
            >
              {categories.map((item) => (
                <option key={item} value={item}>
                  {item.charAt(0).toUpperCase() +
                    item.slice(1)}
                </option>
              ))}
            </select>
          </label>

          <label>
            State / Region
            <input
              value={state}
              disabled={loading || historyLoading}
              onChange={(event) =>
                setState(event.target.value)
              }
              placeholder={
                jurisdiction === "US"
                  ? "e.g. Texas"
                  : "e.g. Telangana"
              }
              maxLength={100}
            />
          </label>
        </section>

        
<DocumentUpload
  key={`${jurisdiction}-${documentVersion}`}
  jurisdiction={jurisdiction}
  onUploaded={handleDocumentUploaded}
  disabled={loading || historyLoading}
/>


<SavedDocuments
  conversationId={activeConversationId}
  refreshKey={documentsRefreshKey}
  selectedDocumentId={documentId}
  disabled={loading || historyLoading}
  onSelectDocument={(id, filename) => {
    setDocumentId(id);
    setActiveDocumentName(filename);
    setError("");
  }}
  onDocumentDeleted={(deletedId) => {
    if (documentId === deletedId) {
      setDocumentId(null);
      setActiveDocumentName("");
      setDocumentVersion((previous) => previous + 1);
    }

    setDocumentsRefreshKey((previous) => previous + 1);
    setError("");
  }}
/>





        {documentId && (
          <div className="document-status">
            <span>
  {activeDocumentName
    ? `Active PDF: ${activeDocumentName}`
    : "PDF selected. Questions will use its contents."}
</span>

            <button
              type="button"
              disabled={loading}
              onClick={handleRemoveDocument}
            >
              Stop using PDF
            </button>
          </div>
        )}

        <ChatWindow
          messages={messages}
          loading={loading}
        />

        {error && (
          <div className="error-banner" role="alert">
            {error}
          </div>
        )}

        <ChatInput
          onSend={handleSend}
          loading={loading || historyLoading}
        />
      </main>
    </div>
  );
}
