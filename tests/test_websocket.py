"""Interactive WebSocket client to test the chat-based shift planning agent."""

import asyncio
import json
import uuid

import websockets

WS_URL = "ws://localhost:9002/ws"


async def receive_and_print(ws: websockets.WebSocketClientProtocol) -> None:
    """Receive events from the server and print them."""
    try:
        async for raw in ws:
            data = json.loads(raw)
            event_type = data.get("type", "?")
            payload = data.get("payload", {})

            if event_type == "chat.completed":
                response = payload.get("response", "")
                print(f"\n[Agent]: {response}\n")
            elif event_type == "status.update":
                message = payload.get("message", "")
                print(f"  [status] {message}")
            elif event_type == "session.joined":
                shift_plan_id = payload.get("shift_plan_id")
                is_new = payload.get("new", False)
                if is_new:
                    print(f"\n[System] Created new shift plan (ID: {shift_plan_id})\n")
                else:
                    print(f"\n[System] Joined shift plan (ID: {shift_plan_id})\n")
            elif event_type == "error":
                print(f"\n[Error]: {payload.get('message', 'Unknown error')}\n")
            else:
                print(f"\n[EVENT] {event_type}")
                print(f"  Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    except websockets.exceptions.ConnectionClosed:
        print("[Connection closed]")


async def main() -> None:
    """Main interactive test client."""
    session_id = str(uuid.uuid4())

    print("=" * 60)
    print("NesPrep - Chat-Based Shift Planning Agent")
    print("=" * 60)
    print()

    try:
        async with websockets.connect(WS_URL) as ws:
            recv_task = asyncio.create_task(receive_and_print(ws))

            print("Connected to server.")
            print()
            print("Commands:")
            print("  /auth <manager_id>  - Set manager ID (required first)")
            print("  /join [shift_plan_id] - Join existing or create new session")
            print("  /quit               - Exit")
            print()
            print("After joining, just type your message to chat with the agent.")
            print("The agent speaks Hebrew and English.")
            print()
            print("Example conversation:")
            print("  > /auth 1")
            print("  > /join")
            print("  > היי, אני רוצה לתכנן את השבוע הבא")
            print("  > העובדים שלי: שקד, דניאל, תהל")
            print("  > שקד יכולה רק א-ג")
            print()

            while True:
                try:
                    line = await asyncio.get_running_loop().run_in_executor(
                        None, lambda: input("> ").strip()
                    )
                except EOFError:
                    break

                if not line:
                    continue

                if line.startswith("/"):
                    parts = line[1:].split(maxsplit=1)
                    cmd = parts[0].lower()

                    if cmd == "quit":
                        break

                    elif cmd == "auth":
                        if len(parts) < 2:
                            print("Usage: /auth <manager_id>")
                            continue
                        manager_id = int(parts[1])
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "auth.set_token",
                                    "manager_id": manager_id,
                                }
                            )
                        )
                        print(f"Set manager ID to {manager_id}")

                    elif cmd == "join":
                        shift_plan_id = None
                        if len(parts) >= 2:
                            try:
                                shift_plan_id = int(parts[1])
                            except ValueError:
                                print("Invalid shift_plan_id")
                                continue

                        msg = {
                            "type": "session.join",
                            "session_id": session_id,
                        }
                        if shift_plan_id:
                            msg["shift_plan_id"] = shift_plan_id

                        await ws.send(json.dumps(msg))

                    else:
                        print(f"Unknown command: /{cmd}")
                        print("Commands: /auth, /join, /quit")

                else:
                    await ws.send(
                        json.dumps(
                            {
                                "type": "chat.send",
                                "session_id": session_id,
                                "message": line,
                            }
                        )
                    )

            recv_task.cancel()
            try:
                await recv_task
            except asyncio.CancelledError:
                pass

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Cannot connect to {WS_URL}: {e}")
        print("Is the server running? (uv run nesprep-ws)")
    except OSError as e:
        print(f"Connection error: {e}")
        print("Is the server running? (uv run nesprep-ws)")


if __name__ == "__main__":
    asyncio.run(main())
