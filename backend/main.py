import random
import string
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="consensus-app backend")

# Allow the Expo dev server / app to call this API during development.
# Tighten this list before deploying anywhere real.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# "Database" (for now)
# ---------------------------------------------------------------------------
# These are just plain Python dicts living in memory. That means everything
# gets wiped if the server restarts — that's fine for building/testing the
# endpoint logic, but this MUST become a real database (e.g. SQLite) before
# this app is used for real, since rooms/votes need to survive a restart.
#
# Shape:
# rooms  = { code: { "id": str, "members": [str, ...] } }
# events = { event_id: { "room_code": str, "title": str, "status": "open"|"closed",
#                         "votes": { user_name: "yes"|"no" } } }
rooms: dict[str, dict] = {}
events: dict[str, dict] = {}


def generate_room_code() -> str:
    """6-character code, easy for people to read out loud and type in."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ---------------------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------------------

class CreateRoomRequest(BaseModel):
    creator_name: str  # whoever's making the room is also its first member


@app.post("/rooms")
def create_room(body: CreateRoomRequest):
    """
    Create a room. This has to live on the backend because the join code
    must come from one authoritative source — otherwise two people could
    generate the same code, or a code that doesn't exist anywhere shared.
    """
    code = generate_room_code()
    while code in rooms:  # extremely unlikely, but avoid collisions
        code = generate_room_code()

    rooms[code] = {
        "id": str(uuid.uuid4()),
        "members": [body.creator_name],
    }
    return {"code": code, **rooms[code]}


class JoinRoomRequest(BaseModel):
    user_name: str


@app.post("/rooms/{code}/join")
def join_room(code: str, body: JoinRoomRequest):
    """A user joins an existing room using its code."""
    room = rooms.get(code)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if body.user_name not in room["members"]:
        room["members"].append(body.user_name)

    return {"code": code, **room}


@app.get("/rooms/{code}")
def get_room(code: str):
    """
    Fetch room info (who's in it, etc). Needed because when someone's
    phone opens, it has no idea what's happened in the room since it
    last checked — it has to ask.
    """
    room = rooms.get(code)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"code": code, **room}


# ---------------------------------------------------------------------------
# Events (the thing being voted on)
# ---------------------------------------------------------------------------

class CreateEventRequest(BaseModel):
    title: str
    proposed_time: str  # ISO 8601 string, e.g. "2026-09-05T19:00:00"
    created_by: str


@app.post("/rooms/{code}/events")
def create_event(code: str, body: CreateEventRequest):
    """Propose an event in a room. Every member needs to see this,
    not just the person who proposed it, so it has to be stored centrally."""
    if code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    event_id = str(uuid.uuid4())
    events[event_id] = {
        "room_code": code,
        "title": body.title,
        "proposed_time": body.proposed_time,
        "created_by": body.created_by,
        "status": "open",  # open -> closed once voting ends
        "votes": {},        # user_name -> "yes" | "no"
    }
    return {"id": event_id, **events[event_id]}


@app.get("/rooms/{code}/events")
def list_events(code: str):
    """List events in a room — a member's phone needs this to catch up
    on what's been proposed since it last checked."""
    if code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    return [
        {"id": event_id, **event}
        for event_id, event in events.items()
        if event["room_code"] == code
    ]


# ---------------------------------------------------------------------------
# Voting
# ---------------------------------------------------------------------------

class VoteRequest(BaseModel):
    user_name: str
    vote: str  # "yes" or "no"


@app.post("/events/{event_id}/vote")
def cast_vote(event_id: str, body: VoteRequest):
    """
    Cast a yes/no vote. This must go through the backend, not just live on
    the voter's phone, because everyone else's phone needs to see the
    combined tally, and a user shouldn't be able to vote twice by accident.
    """
    event = events.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event["status"] != "open":
        raise HTTPException(status_code=400, detail="Voting is closed for this event")
    if body.vote not in ("yes", "no"):
        raise HTTPException(status_code=400, detail="vote must be 'yes' or 'no'")

    event["votes"][body.user_name] = body.vote  # overwrite if they already voted
    return {"id": event_id, **event}


@app.get("/events/{event_id}/votes")
def get_votes(event_id: str):
    """Current tally, so phones show real results instead of guessing."""
    event = events.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    yes = sum(1 for v in event["votes"].values() if v == "yes")
    no = sum(1 for v in event["votes"].values() if v == "no")
    return {"yes": yes, "no": no, "votes": event["votes"]}


# ---------------------------------------------------------------------------
# Closing voting
# ---------------------------------------------------------------------------
# Calendar file generation (.ics) was here but is cut for now — not needed
# for the MVP. Add it back once voting/rooms feel solid.

@app.post("/events/{event_id}/close")
def close_event(event_id: str):
    """
    Lock voting so no more votes come in. Decision of *who* is allowed to
    close it (only the proposer? anyone? automatic deadline?) is left open
    for now — right now anyone can close it, tighten this later.
    """
    event = events.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    event["status"] = "closed"
    return {"id": event_id, **event}
