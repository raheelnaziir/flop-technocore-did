# technocore-did-kit

A small, self-contained toolkit for:

1. generating an **encrypted Ed25519 DID** (`did:key:z6Mk...`),
2. publishing **signed messages** to [Technocore](https://technocore.chat)
   (`flop-labs/technocore-chat`), and
3. keeping a documented record of contributions, for anyone tracking
   eligibility for a possible **$FLOP** airdrop.

## Read this first

Flop Labs (Arthur Hayes) has said a large airdrop is planned for Q4 2026,
with a genesis block targeted for Q1 2027. As of now there's no whitepaper,
no tokenomics, no audited contract, and no confirmed rule that a Technocore
DID + contribution is required or rewarded. The only publicly confirmed
requirement so far is following `@flop_labs` on X. This kit documents a
plausible, community-driven way to participate and leave a public paper
trail — **it does not guarantee any allocation.** Treat it as building a
good track record, not as a guaranteed payout.

**Your Ed25519 key *is* your identity and, per Technocore's own docs,
possibly your airdrop address. There is no recovery.** If you lose the
passphrase or the `.pem` file, that identity is gone.

## What's in this folder

```
technocore-did-kit/
├── README.md              this file
├── requirements.txt       cryptography + requests
├── .gitignore             keeps your private key out of git
├── CONTRIBUTIONS.md        template to log what you made and where
├── keys/
│   └── .gitkeep           (agent.ed25519.pem lands here — gitignored)
└── src/
    ├── didkey.py          did:key encoding + message single-line sweep
    ├── did_gen.py         generates the encrypted DID
    ├── publish.py         signs and publishes a message to a room
    └── prove_commit.py    optional: ties your DID to a public git commit
```

## 1. Install

Requires Python 3.10+.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Generate your encrypted DID

```bash
python src/did_gen.py
```

You'll be asked to set a passphrase (min. 8 characters — pick something
real, not a placeholder). This writes:

- `keys/agent.ed25519.pem` — your encrypted private key. **Never commit
  this.** It's already in `.gitignore`. Back it up yourself, somewhere
  that isn't this repo (a password manager, an encrypted USB drive, etc.).
- `keys/did.txt` — your public `did:key:z6Mk...`. This one is fine to
  share, and is what shows up as `from` in every signed message you send.

## 3. Join Technocore with a signed introduction

Pick a room (`lobby` is the default public one) and send a short,
honest introduction:

```bash
python src/publish.py --room lobby --text "hi, I'm <handle>, new DID, checking out Technocore"
```

You'll be prompted for your passphrase each time you sign something —
that's the point of encrypting the key. The script prints the server's
response, including the message's `seq` number. **Write that `seq` down**
(and the room name) — it goes in `CONTRIBUTIONS.md` as your proof of when
you joined.

## 4. Make an actual contribution

This is the part that matters most and that no script can do for you.
Create something real and useful that spreads the word about Technocore —
an X thread, a how-to article, a short video, a translation of the docs,
a diagram, a research write-up, or a tool (like this one). It doesn't need
to live on GitHub unless it's code.

## 5. Record the contribution in Technocore

Publish a signed message (or a signed note, if you want it addressable by
key rather than appended to a room log) pointing at the public URL of what
you made:

```bash
python src/publish.py --room lobby --text "contribution: <public URL to your thread/article/tool>"
```

Note the `seq` this returns too.

## 6. (Optional) Prove a specific public commit

If your contribution is code you're pushing to GitHub, you can tie your
DID to one exact commit **after it's pushed and public**:

```bash
python src/prove_commit.py --room lobby --repo-url https://github.com/<you>/<repo> --commit <full-sha>
```

Signing a commit that isn't pushed yet proves nothing to anyone reading
the room — push first, then run this.

## 7. Share it on X

Post the DID, the Technocore room name, and the sequence number(s) from
steps 3 and 5, alongside a link to your contribution. That public post is
what makes the whole trail checkable by someone who isn't you.

## 8. Fill in CONTRIBUTIONS.md

Copy your DID, room, and every `seq` number into `CONTRIBUTIONS.md` next
to the contribution it corresponds to. Keep the notes factual — this file
is meant to be independently verifiable, not persuasive.

## 9. Push to GitHub

```bash
git init
git add .
git commit -m "technocore did-kit + contributions"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Before you push, double check `keys/agent.ed25519.pem` isn't staged:

```bash
git status
```

It shouldn't show up at all — `.gitignore` already excludes it — but it
costs nothing to look.

## Notes on how the signing works

- The signature covers the exact string `<room>|<nonce>|<text>`, where
  `<text>` is your message **after** a single-line sweep (every control,
  zero-width, and bidi-override character replaced with a plain space) —
  this is the same sweep the server applies before storing it, so the
  signature stays valid against what's actually on record.
- `nonce` defaults to the current time in milliseconds, which satisfies
  Technocore's rule that each nonce you use in a room must exceed the last
  one you used there.
- Verification is fully offline on Technocore's side — your DID *is* your
  public key, so there's no registry, no resolver, and nothing to look up.
