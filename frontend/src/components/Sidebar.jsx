
import { Plus, Scale, BookOpen, ShieldCheck, MessageSquare, Trash2 } from "lucide-react";

export default function Sidebar({
  conversations = [],
  activeConversationId = null,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  loading = false,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <Scale size={25} />
        <div>
          <h2>Legal AI</h2>
          <p>US & India</p>
        </div>
      </div>

      <button
        type="button"
        className="new-chat-button"
        onClick={onNewChat}
        disabled={loading}
      >
        <Plus size={18} />
        New Conversation
      </button>

      <div className="sidebar-section">
        <p className="sidebar-section-title">CHAT HISTORY</p>

        {conversations.length === 0 ? (
          <p className="sidebar-empty">
            No saved conversations yet.
          </p>
        ) : (
          <div className="conversation-list">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={
                  activeConversationId === conversation.id
                    ? "conversation-item active"
                    : "conversation-item"
                }
              >
                <button
                  type="button"
                  className="conversation-open"
                  disabled={loading}
                  onClick={() =>
                    onSelectConversation(conversation.id)
                  }
                  title={conversation.title}
                >
                  <MessageSquare size={16} />
                  <span>{conversation.title}</span>
                </button>

                <button
                  type="button"
                  className="conversation-delete"
                  disabled={loading}
                  onClick={() => {
                    if (
                      window.confirm(
                        "Delete this conversation permanently?"
                      )
                    ) {
                      onDeleteConversation(conversation.id);
                    }
                  }}
                  title="Delete conversation"
                  aria-label={`Delete ${conversation.title}`}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-section">
        <p className="sidebar-section-title">LEGAL ASSISTANT</p>

        <div className="sidebar-info-item">
          <BookOpen size={17} />
          <span>Legal Information</span>
        </div>

        <div className="sidebar-info-item">
          <ShieldCheck size={17} />
          <span>Jurisdiction Aware</span>
        </div>
      </div>

      <div className="sidebar-footer">
        <p>Educational legal information only.</p>
        <p>Not a substitute for an attorney.</p>
      </div>
    </aside>
  );
}
