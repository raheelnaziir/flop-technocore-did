#!/usr/bin/env python3
"""
did_gen.py — generate a brand-new, password-encrypted Ed25519 identity and
derive its did:key:z6Mk... for use with Technocore (technocore.chat).

Usage:
    python src/did_gen.py

Produces:
    keys/agent.ed25519.pem   (PKCS#8, password-encrypted, PEM)
    keys/did.txt             (the derived did:key, plaintext, safe to share)

There is NO password recovery. If you lose the passphrase or the .pem file,
that identity — and anything tied to it (rooms, contributions, an eventual
airdrop allocation) — is gone for good. Back the .pem file up somewhere
safe that is NOT the git repo you're about to push.
"""

import getpass
import os
import stat
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, os.path.dirname(__file__))
from didkey import pubkey_to_did  # noqa: E402

KEYS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys")
KEY_PATH = os.path.join(KEYS_DIR, "agent.ed25519.pem")
DID_PATH = os.path.join(KEYS_DIR, "did.txt")


def main() -> None:
    if os.path.exists(KEY_PATH):
        print(f"A key already exists at {KEY_PATH}.")
        print("Refusing to overwrite it. Delete it yourself first if you really want a new identity.")
        sys.exit(1)

    os.makedirs(KEYS_DIR, exist_ok=True)
    # best-effort restrictive permissions; no-op on Windows filesystems that
    # don't support POSIX bits, harmless either way
    try:
        os.chmod(KEYS_DIR, stat.S_IRWXU)  # 0700
    except (NotImplementedError, OSError):
        pass

    print("Generating a new Ed25519 keypair locally (nothing leaves this machine)...")
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    raw_pub = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    did = pubkey_to_did(raw_pub)

    print()
    print("Choose a passphrase to encrypt the private key file.")
    print("This is used every time you sign a message — pick something you can retype.")
    while True:
        pw1 = getpass.getpass("Passphrase: ")
        if len(pw1) < 8:
            print("Use at least 8 characters.")
            continue
        pw2 = getpass.getpass("Confirm passphrase: ")
        if pw1 != pw2:
            print("Passphrases didn't match, try again.")
            continue
        break

    encrypted_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(pw1.encode("utf-8")),
    )

    with open(KEY_PATH, "wb") as f:
        f.write(encrypted_pem)
    try:
        os.chmod(KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except (NotImplementedError, OSError):
        pass

    with open(DID_PATH, "w") as f:
        f.write(did + "\n")

    print()
    print("Done.")
    print(f"  Encrypted private key: {KEY_PATH}")
    print(f"  Public DID:            {did}")
    print()
    print("keys/ is already listed in .gitignore — double check it never gets")
    print("committed. Only did.txt (public) is meant to be shareable; the .pem is not.")


if __name__ == "__main__":
    main()
