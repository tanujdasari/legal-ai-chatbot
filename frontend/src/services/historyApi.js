
const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

async function historyRequest(path, options = {}) {
  const response = await fetch(
    `${API_URL}/api/history${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    }
  );

  if (!response.ok) {
    let message = `History request failed (${response.status})`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      } else if (Array.isArray(error.detail)) {
        message = error.detail
          .map((item) => item.msg)
          .join("; ");
      }
    } catch {
      // Keep the HTTP status error.
    }

    throw new Error(message);
  }

  // DELETE may return 204 No Content.
  if (response.status === 204) {
    return null;
  }

  const text = await response.text();

  if (!text) {
    return null;
  }

  return JSON.parse(text);
}

export function getConversations() {
  return historyRequest("/conversations");
}

export function createConversation(payload) {
  return historyRequest("/conversations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getConversation(conversationId) {
  return historyRequest(
    `/conversations/${encodeURIComponent(conversationId)}`
  );
}

export function saveMessage(conversationId, payload) {
  return historyRequest(
    `/conversations/${encodeURIComponent(conversationId)}/messages`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function deleteConversation(conversationId) {
  return historyRequest(
    `/conversations/${encodeURIComponent(conversationId)}`,
    {
      method: "DELETE",
    }
  );
}
