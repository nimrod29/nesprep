"""Server-to-client event type constants."""


class EventTypes:
    """Event type strings sent from server to client."""

    SESSION_JOINED = "session.joined"
    CHAT_STARTED = "chat.started"
    CHAT_COMPLETED = "chat.completed"
    STATUS_UPDATE = "status.update"
    PLAN_COMPLETED = "plan.completed"
    ERROR = "error"
