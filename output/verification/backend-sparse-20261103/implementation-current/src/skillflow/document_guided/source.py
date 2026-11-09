"""Exact frozen-source selection, without inferred semantic connections."""
from collections.abc import Mapping
from copy import deepcopy
import re

from skillflow.common.source_evidence import (
    extract_source_lines, source_lines, validate_source_ref,
)


def source_packet(files: Mapping[str, str], spans=None) -> dict:
    """None selects all readable source; [] selects none. Preserve original bytes
    after decoding, including line endings. Navigation is not semantic coverage.
    Missing and binary dependencies remain caller-visible package boundaries.
    """
    if not isinstance(files, Mapping) or not files:
        raise ValueError("A frozen file table is required")
    if any(not isinstance(name, str) or not name or type(text) is not str
           for name, text in files.items()):
        raise ValueError("The file table must contain exact logical names and text")
    lines = {name: source_lines(text) for name, text in files.items()}
    if spans is None:
        spans = [{"file": name, "start_line": 1, "end_line": len(rows)}
                 for name, rows in lines.items() if rows]
    selected = {name: set() for name in files}
    for span in spans:
        parsed = validate_source_ref(span, files)
        selected[parsed.file].update(range(parsed.start_line, parsed.end_line + 1))

    def intervals(numbers):
        result = []
        for number in sorted(numbers):
            if result and number == result[-1][1] + 1:
                result[-1][1] = number
            else:
                result.append([number, number])
        return result

    ranges, unreferenced = [], []
    for name, rows in lines.items():
        for start, end in intervals(selected[name]):
            ranges.append({"file": name, "start_line": start, "end_line": end,
                           "text": extract_source_lines(files[name], start, end)})
        for start, end in intervals(set(range(1, len(rows) + 1)) - selected[name]):
            unreferenced.append({"file": name, "start_line": start, "end_line": end})
    return {"files": [{"file": name, "line_count": len(rows)} for name, rows in lines.items()],
            "ranges": ranges, "unreferenced_ranges": unreferenced}


def render_source(packet):
    parts = ["File navigation (not proof of semantic coverage):"]
    parts.extend(f"- {row['file']} ({row['line_count']} physical lines)" for row in packet["files"])
    parts.extend("Selection note: " + note for note in packet.get("selection_notes", []))
    for span in packet["ranges"]:
        parts.append(f"\nSOURCE {span['file']}:{span['start_line']}-{span['end_line']}\n" +
                     "".join(f"{number}: {line}" for number, line in enumerate(
                         source_lines(span["text"]), span["start_line"])))
    return "\n".join(parts)


def select_document_source(files, documents, *, spans=None):
    """Select explicit document references, never inferred import relationships.

    Working documents use ``skill/path.ext:12-18`` (or a complete file name).
    A mentioned file without a usable range is provided in full. If no document
    references source, the whole source is retained rather than silently lost.
    Explicit caller-supplied spans remain strict, unlike prose navigation.
    """
    source_packet(files, [])  # Validate the frozen table even with no references.
    text = "\n".join(documents.values()) if isinstance(documents, Mapping) else str(documents)
    notes, selected, references = [], [], 0
    if spans is not None:
        for span in spans:
            parsed = validate_source_ref(span, files)
            selected.append({"file": parsed.file, "start_line": parsed.start_line, "end_line": parsed.end_line})
        references = len(selected)
    # Unknown names are not resolved by basename, similarity or filesystem access.
    for match in re.finditer(r"(?<![\w/])skill/[^\s`\"'<>\[\](){}:;,]+", text):
        name = match.group().rstrip(".")
        if name not in files:
            raise ValueError("Working document references an unknown frozen file: " + name)
    for name, content in files.items():
        pattern = re.compile(r"(?<![\w/])" + re.escape(name) + r"(?![\w/.-])")
        matches = list(pattern.finditer(text))
        if not matches:
            continue
        references += len(matches)
        length = len(source_lines(content))
        for match in matches:
            suffix = text[match.end():]
            located = re.match(r":(?:L)?(\d+)(?:[-–](?:L)?(\d+))?(?!\d)", suffix)
            start = int(located[1]) if located else 0
            end = int(located[2] or located[1]) if located else 0
            if located and 1 <= start <= end <= length:
                selected.append({"file": name, "start_line": start, "end_line": end})
            elif length:
                selected.append({"file": name, "start_line": 1, "end_line": length})
                notes.append("Included the complete referenced file because its physical range was absent or unusable: " + name)
    if not references:
        packet = source_packet(files)
        packet["selection_notes"] = ["No explicit source references were available; retained the complete readable source."]
        return packet
    # Main Skill instructions must not disappear in local views.
    for name in ("skill/SKILL.md", "SKILL.md"):
        if name in files and source_lines(files[name]):
            selected.append({"file": name, "start_line": 1, "end_line": len(source_lines(files[name]))})
    packet = source_packet(files, selected)
    packet["selection_notes"] = list(dict.fromkeys(notes))
    return packet


def prompt_cfg(cfg, *, packet=None):
    """Omit only code already supplied byte-for-byte in the displayed source.

    No source packet means no omission. This is duplication removal, not a
    lookup for code ownership or a claim of semantic equivalence.
    """
    result = deepcopy(cfg)
    graph = result.get("cfg", result)
    blocks = graph.get("blocks", [])
    for block in blocks.values() if isinstance(blocks, dict) else blocks:
        for instruction in block.get("instructions", []):
            metadata = instruction.get("metadata", {})
            code = metadata.get("script_content")
            if (type(code) is str and code and packet is not None
                    and any(code in span["text"] for span in packet["ranges"])):
                metadata.pop("script_content")
    return result


def select_fragment_source(files, processing):
    """Use typed evidence positions, never runtime literals or arbitrary prose."""
    spans = []

    def visit(value):
        if isinstance(value, dict):
            if value.get("kind") == "literal" or value.get("type") == "literal":
                return
            for key, child in value.items():
                if key in {"literal_value", "metadata"}:
                    continue
                if key == "evidences" and isinstance(child, list):
                    for evidence in child:
                        if isinstance(evidence, dict) and {"file", "start_line", "end_line"} <= evidence.keys():
                            parsed = validate_source_ref({name: evidence[name] for name in
                                ("file", "start_line", "end_line")}, files)
                            spans.append({"file": parsed.file, "start_line": parsed.start_line, "end_line": parsed.end_line})
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(processing)
    if not spans:
        packet = source_packet(files)
        packet["selection_notes"] = ["No typed source evidence was available; retained the complete readable source."]
        return packet
    for name in ("skill/SKILL.md", "SKILL.md"):
        if name in files and source_lines(files[name]):
            spans.append({"file": name, "start_line": 1, "end_line": len(source_lines(files[name]))})
    packet = source_packet(files, spans)
    packet["selection_notes"] = ["Selected exact typed evidence ranges and complete main Skill; runtime literals do not select source."]
    return packet


def copy_script_content(candidate, instruction_ref, span, *, files):
    """Copy only a model-selected instruction and exact frozen source range.

    The selection belongs to technical request bookkeeping, not a new CFG
    field. Never search by file extension, function name, or code similarity.
    """
    ref = validate_source_ref(span, files)
    text = extract_source_lines(files[ref.file], ref.start_line, ref.end_line)
    result = deepcopy(candidate)
    matches = [ir for block in result.get("blocks", []) for ir in block.get("instructions", [])
               if ir.get("instruction_ref") == instruction_ref]
    if len(matches) != 1:
        raise ValueError("Script copying requires one exact existing instruction")
    metadata = matches[0].setdefault("metadata", {})
    if "script_content" in metadata and metadata["script_content"] != text:
        raise ValueError("Existing script content differs from the explicit frozen range")
    metadata["script_content"] = text
    return result
