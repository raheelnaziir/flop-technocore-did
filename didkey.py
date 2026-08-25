"""
didkey.py — minimal did:key:z6Mk... helpers for Ed25519.

No dependency on the `base58` package: base58btc is ~20 lines and this way
the whole kit only needs `cryptography` + `requests`.

did:key encoding for Ed25519 (per the did:key spec):
    multicodec_prefix (0xed, 0x01) + 32-byte raw public key
    -> base58btc encode
    -> prefix with 'z' (multibase code for base58btc)
    -> prefix with 'did:key:'
"""

from __future__ import annotations

_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n > 0:
        n, rem = divmod(n, 58)
        out = _ALPHABET[rem] + out
    # preserve leading zero bytes as leading '1's
    n_leading_zeros = len(data) - len(data.lstrip(b"\x00"))
    return "1" * n_leading_zeros + (out or "1" if data else "")


def pubkey_to_did(raw_pubkey: bytes) -> str:
    """raw_pubkey: 32-byte raw Ed25519 public key bytes."""
    if len(raw_pubkey) != 32:
        raise ValueError("Ed25519 public key must be exactly 32 bytes")
    multicodec_prefixed = bytes([0xED, 0x01]) + raw_pubkey
    return "did:key:z" + b58encode(multicodec_prefixed)


def sweep_single_line(text: str) -> str:
    """Mirrors the server's single-line sweep so the signature covers the
    exact bytes that end up stored: every control / format / zero-width /
    bidi-override character becomes a plain space before signing."""
    out = []
    for ch in text:
        cp = ord(ch)
        is_control = cp < 0x20 or cp == 0x7F
        is_format_or_bidi = (
            0x200B <= cp <= 0x200F  # zero-width space/joiners, LRM/RLM
            or 0x202A <= cp <= 0x202E  # bidi embedding/override controls
            or cp == 0x2060  # word joiner
            or 0x2066 <= cp <= 0x2069  # bidi isolates
            or cp == 0xFEFF  # BOM / zero-width no-break space
        )
        out.append(" " if (is_control or is_format_or_bidi) else ch)
    return "".join(out)
