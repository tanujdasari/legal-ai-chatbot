import { useEffect, useRef } from "react";
import { Bot, UserRound, Scale } from "lucide-react";

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="welcome">
          <Scale size={48} />
          <h1>Welcome to Legal AI Assistant</h1>
          <p>
            Explore legal concepts and procedures in
            the United States and India.
          </p>
          <span>
            Select your jurisdiction and ask a question
            to get started.
          </span>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.role}`}
        >
          <div className="avatar">
            {message.role === "user" ? (
              <UserRound size={19} />
            ) : (
              <Bot size={19} />
            )}
          </div>

          <div className="message-content">
            <div className="message-role">
              {message.role === "user"
                ? "You"
                : "Legal AI Assistant"}
            </div>

            <div className="message-text">
              {message.content}
            </div>

            {message.disclaimer && (
              <div className="message-disclaimer">
                {message.disclaimer}
              </div>
            )}

            {message.sources?.length > 0 && (
              <div className="message-sources">
                <strong>Sources</strong>
                <ul>
                  {message.sources.map((source, index) => (
                    <li key={index}>{source}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      ))}

      {loading && (
        <div className="message assistant">
          <div className="avatar">
            <Bot size={19} />
          </div>
          <div className="message-content">
            <div className="message-role">
              Legal AI Assistant
            </div>
            <div className="typing">
              Generating response...
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}