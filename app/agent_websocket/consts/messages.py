"""Client-to-server message type constants."""


class ClientMessageTypes:
    """Message type strings sent from client to server."""

    AUTH_SET_TOKEN = "auth.set_token"
    SESSION_JOIN = "session.join"
    CHAT_SEND = "chat.send"
