"""Measure the exact model delivery without changing source or semantic inputs."""
import hashlib


IDENTITY = "skillflow-delivery-size-v1"
_HEADINGS = (
    "STEP RESPONSIBILITY",
    "PREVIOUS WORK",
    "GLOBAL REQUIREMENTS AND LIMITATIONS",
    "RELATED SOURCE",
    "OUTPUT REQUIREMENTS",
)


def _size(text):
    encoded = text.encode("utf-8")
    return {"characters": len(text), "utf8_bytes": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest()}


def inspect_delivery(prompt, *, prefix="", max_characters):
    """Count Unicode code points including the adapter prefix.

    Sections are descriptive byte-bound slices. Source citations and logical
    identities remain the responsibility of the existing strict validators.
    """
    if not isinstance(prompt, str) or not prompt.strip() or not isinstance(prefix, str):
        raise ValueError("Delivery inspection requires a nonempty prompt and a string prefix")
    if type(max_characters) is not int or max_characters < 1:
        raise ValueError("The delivery character limit must be a positive integer")
    sections = {"adapter_prefix": _size(prefix)}
    positions, cursor = [], 0
    for heading in _HEADINGS:
        marker = heading + "\n"
        start = prompt.find(marker, cursor)
        if start < 0 or (start and not prompt[:start].endswith("\n\n")):
            positions = []
            break
        positions.append((heading.lower().replace(" ", "_"), start))
        cursor = start + len(marker)
    if positions:
        if positions[0][1]:
            sections["prompt_prefix"] = _size(prompt[:positions[0][1]])
        for index, (name, start) in enumerate(positions):
            end = positions[index + 1][1] if index + 1 < len(positions) else len(prompt)
            sections[name] = _size(prompt[start:end])
    else:
        sections["prompt"] = _size(prompt)
    delivery = _size(prefix + prompt)
    return {"identity": IDENTITY, "metric": "unicode_codepoints", **delivery,
            "max_characters": max_characters,
            "excess_characters": max(0, delivery["characters"] - max_characters),
            "status": "within_limit" if delivery["characters"] <= max_characters else "input_too_large",
            "sections": sections}
