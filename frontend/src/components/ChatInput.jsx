import { useState } from "react";
import { Send } from "lucide-react";

export default function ChatInput({ onSend, loading }) {
  const [question, setQuestion] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const trimmed = question.trim();

    if (trimmed.length < 5 || loading) {
      return;
    }

    onSend(trimmed);
    setQuestion("");
  }

  return (
    <form className="chat-input-area" onSubmit={handleSubmit}>
      <div className="chat-input-box">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask your legal question..."
          rows={2}
          maxLength={5000}
          disabled={loading}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />

        <button
          type="submit"
          disabled={loading || question.trim().length < 5}
          aria-label="Send question"
        >
          <Send size={20} />
        </button>
      </div>

      <p className="input-note">
        AI responses may be inaccurate or outdated.
        Verify important information with official sources.
      </p>
    </form>
  );
}