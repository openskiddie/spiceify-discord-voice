import asyncio
import websockets
import json

# OBS StreamKit's Client ID (Whitelisted by Discord for Voice RPC scopes)
DISCORD_CLIENT_ID = "207646673902501888"

# Discord's local RPC runs on port 6463 by default
DISCORD_RPC_URL = f"ws://127.0.0.1:6463/?v=1&client_id={DISCORD_CLIENT_ID}"

# Global state to share with Spicetify
vc_state = {
    "channel_name": "Not in VC",
    "members": {}  # Maps user_id -> {"name": str, "speaking": bool}
}
spicetify_clients = set()


# --- SPICETIFY SERVER (Sends data to Spotify) ---
async def notify_spicetify():
    if not spicetify_clients:
        return

    payload = {
        "channel_name": vc_state["channel_name"],
        "members": list(vc_state["members"].values())
    }
    message = json.dumps(payload)

    # Track disconnected sockets to clean them up safely
    disconnected = set()

    for ws in spicetify_clients:
        try:
            await ws.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.add(ws)

    # Clean up any dead connections
    if disconnected:
        spicetify_clients.difference_update(disconnected)


async def spicetify_server(websocket):
    spicetify_clients.add(websocket)
    try:
        await notify_spicetify()  # Push current state immediately upon connection
        await asyncio.Future()  # Keep connection open
    finally:
        spicetify_clients.remove(websocket)


# --- DISCORD IPC CLIENT (Gets data from Discord) ---
# --- DISCORD IPC CLIENT (Gets data from Discord) ---
async def discord_ipc_client():
    while True:
        try:
            async with websockets.connect(DISCORD_RPC_URL, origin="https://streamkit.discord.com") as ws:
                print("Connected to Discord Local RPC!")

                async for message in ws:
                    data = json.loads(message)
                    evt = data.get("evt")
                    payload = data.get("data", {})
                    nonce = data.get("nonce")  # <--- THIS WAS MISSING!

                    # Keep the debug print so we can see what happens next!
                    print(f"RAW DISCORD DATA: {data}")

                    # 1. WAIT FOR HANDSHAKE -> AUTHENTICATE
                    if evt == "READY":
                        print("Authenticating with Discord...")
                        await ws.send(json.dumps({
                            "cmd": "AUTHENTICATE",
                            "args": {
                                "access_token": "YOUR_TOKEN_HERE"
                            },
                            "nonce": "auth"
                        }))

                    # 2. WAIT FOR AUTH CONFIRMATION -> SUBSCRIBE TO CHANNEL UPDATES (THIS WAS MISSING!)
                    elif nonce == "auth":
                        if evt == "ERROR":
                            print(f"Auth failed! Check your token: {payload}")
                        else:
                            print("Authentication successful! Subscribing to voice events...")
                            await ws.send(json.dumps({
                                "cmd": "SUBSCRIBE",
                                "evt": "VOICE_CHANNEL_SELECT",
                                "nonce": "init"
                            }))

                    # 3. HANDLE CHANNEL SELECTION
                    elif evt == "VOICE_CHANNEL_SELECT":
                        channel_id = payload.get("channel_id")
                        vc_state["members"].clear()

                        if channel_id:
                            vc_state["channel_name"] = "Connected to VC"

                            events = ["VOICE_STATE_CREATE", "VOICE_STATE_UPDATE", "VOICE_STATE_DELETE",
                                      "SPEAKING_START", "SPEAKING_STOP"]
                            for e in events:
                                await ws.send(json.dumps({
                                    "cmd": "SUBSCRIBE",
                                    "evt": e,
                                    "args": {"channel_id": channel_id},
                                    "nonce": f"sub_{e}"
                                }))
                        else:
                            vc_state["channel_name"] = "Not in VC"

                        await notify_spicetify()

                    # 4. HANDLE USERS AND SPEAKING STATES
                    elif evt in ["VOICE_STATE_CREATE", "VOICE_STATE_UPDATE"]:
                        user = payload.get("user", {})
                        user_id = user.get("id")
                        name = user.get("global_name") or user.get("username")

                        if user_id not in vc_state["members"]:
                            vc_state["members"][user_id] = {"name": name, "speaking": False}
                        await notify_spicetify()

                    elif evt == "VOICE_STATE_DELETE":
                        user_id = payload.get("user", {}).get("id")
                        vc_state["members"].pop(user_id, None)
                        await notify_spicetify()

                    elif evt == "SPEAKING_START":
                        user_id = payload.get("user_id")
                        if user_id in vc_state["members"]:
                            vc_state["members"][user_id]["speaking"] = True
                            await notify_spicetify()

                    elif evt == "SPEAKING_STOP":
                        user_id = payload.get("user_id")
                        if user_id in vc_state["members"]:
                            vc_state["members"][user_id]["speaking"] = False
                            await notify_spicetify()

        except Exception as e:
            print(f"Discord IPC connection lost. Retrying in 5s... ({e})")
            await asyncio.sleep(5)


# --- MAIN EVENT LOOP ---
async def main():
    # Start the Spicetify WebSocket Server on port 8765
    server = await websockets.serve(spicetify_server, "127.0.0.1", 8765)
    print("Spicetify Bridge listening on ws://127.0.0.1:8765")

    # Run the Discord IPC connection continuously
    await discord_ipc_client()


if __name__ == "__main__":
    asyncio.run(main())