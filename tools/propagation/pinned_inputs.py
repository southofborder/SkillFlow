"""Byte-only provenance checks for explicitly pinned historical source packages.

Historical snapshots are not loaded, upgraded or resumed. Their original receipt
is checked against the new raw-input inspection before a new run is prepared.
"""
from skillflow.common.recording import canonical_sha256


def _content_boundaries(value):
    """Compare classified content, not a producer's explanatory wording.

    The original notice remains protected by the full receipt digest. Other
    boundary keys are retained so unknown or changed boundaries cannot be
    silently ignored by this byte-only historical-input check.
    """
    if (not isinstance(value, dict) or not isinstance(value.get("notice"), str)
            or any(not isinstance(value.get(key), list)
                   or any(not isinstance(path, str) for path in value[key])
                   for key in ("binary_files", "uninterpreted_code_files"))):
        raise ValueError("historical source boundary receipt has an invalid structure")
    return {key: item for key, item in value.items() if key != "notice"}


def verify_historical_byte_receipt(receipt, observed):
    expected = canonical_sha256({key: value for key, value in receipt.items() if key != "snapshot_sha256"})
    if receipt.get("snapshot_sha256") != expected:
        raise ValueError("historical source receipt digest differs")
    if (any(receipt.get(key) != observed[key] for key in
            ("files", "package_bytes_sha256", "source_sha256"))
            or _content_boundaries(receipt.get("boundaries")) != _content_boundaries(observed.get("boundaries"))):
        raise ValueError("historical package bytes or decoded source differ from the frozen receipt")
