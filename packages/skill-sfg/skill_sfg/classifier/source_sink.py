"""Source/sink classification — port of src/classifier/source-sink.js."""

from __future__ import annotations


def create_user_query_source() -> dict:
    """Port of createUserQuerySource (source-sink.js:11-28).

    The implicit user query is the initial data source that triggers Skill
    activation in OpenClaw.
    """
    return {
        "name": "user.query",
        "action": "query",
        "type": "builtin_call",
        "description": "User query that triggers Skill activation",
        "input": {},
        "output": {
            "query_text": {"type": "string"},
            "intent": {"type": "string"},
        },
        "location": {
            "file": "OpenClaw Runtime",
            "line": 0,
            "section": "Skill Activation Flow",
        },
    }
