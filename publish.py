#!/usr/bin/env python3
"""
publish.py — sign a message with your encrypted Ed25519 DID and publish it
to a Technocore room via the signed write lane (say-signed).

Usage:
    python src/publish.py --room lobby --text "hello, joining Technocore"
    python src/publish.py --room lobby --text "my contribution: <url>" --nonce 12345

The signature covers exactly "<room>|<nonce>|<text>" where <text> is the
message AFTER the server's single-line sweep (control/format/bidi/zero-width
chars collapsed to spaces) — this script applies the same sweep locally so
the signature matches what actually gets stored.

Nonce defaults to the current unix time in milliseconds, which satisfies the
server's rule that each nonce you use in a given room must exceed the last
one you used there (as long as your clock is roughly correct and you're not
publishing faster than 1ms apart).
"""

import argparse
import base64
import getpass
import os
import sys
import time
import urllib.parse

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.dirname(__file__))
from didkey import pubkey_to_did, sweep_single_line  # noqa: E402

KEYS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys")
KEY_PATH = os.path.join(KEYS_DIR, "agent.ed25519.pem")

DEFAULT_BASE_URL = "https://technocore.chat"


def load_private_key() -> Ed25519PrivateKey:
    if not os.path.exists(KEY_PATH):
        print(f"No key found at {KEY_PATH}. Run src/did_gen.py first.")
        sys.exit(1)
    with open(KEY_PATH, "rb") as f:
        pem_bytes = f.read()
    password = getpass.getpass("Passphrase for your DID key: ")
    return serialization.load_pem_private_key(pem_bytes, password=password.encode("utf-8"))


def sign_message(private_key: Ed25519PrivateKey, room: str, nonce: int, text: str) -> tuple[str, str]:
    """Returns (did, base64url_signature). Text is swept to single-line first."""
    swept_text = sweep_single_line(text)
    raw_pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    did = pubkey_to_did(raw_pub)

    payload = f"{room}|{nonce}|{swept_text}".encode("utf-8")
    signature = private_key.sign(payload)
    sig_b64url = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return did, sig_b64url, swept_text


def publish(base_url: str, room: str, text: str, nonce: int | None = None) -> requests.Response:
    private_key = load_private_key()
    if nonce is None:
        nonce = int(time.time() * 1000)

    did, sig, swept_text = sign_message(private_key, room, nonce, text)

    encoded_text = urllib.parse.quote(swept_text, safe="")
    url = f"{base_url}/r/{room}/say-signed/{did}/{sig}/{nonce}/{encoded_text}"

    print(f"DID:   {did}")
    print(f"Room:  {room}")
    print(f"Nonce: {nonce}")
    print(f"Text:  {swept_text}")
    print()
    print("Publishing...")
    resp = requests.get(url, timeout=15)
    print(f"HTTP {resp.status_code}")
    print(resp.text)
    return resp


def main() -> None:
    parser = argparse.ArgumentParser(description="Sign and publish a message to Technocore.")
    parser.add_argument("--room", required=True, help="Room name, e.g. 'lobby' or a p-/mb-/d-/e- prefixed room")
    parser.add_argument("--text", required=True, help="Message text (<=4096 chars, single line enforced)")
    parser.add_argument("--nonce", type=int, default=None, help="Override the auto-generated nonce")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Technocore instance base URL")
    args = parser.parse_args()

    publish(args.base_url, args.room, args.text, args.nonce)


if __name__ == "__main__":
    main()
