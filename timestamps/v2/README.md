# OpenTimestamps proofs for version 2 (commit 6d42bb9)

These files show that the state of this repository at commit `6d42bb988bd60ca5e7928b2be77b3e24fda991c5` (version 2: v6 ≥ 51) existed at the time recorded
by OpenTimestamps. Only hashes were sent to the public calendars, never the content.

| file | what it attests |
|---|---|
| `COMMIT.txt` + `COMMIT.txt.ots` | the commit hash, its tree hash and the SHA-256 of the version 2 note, as listed |
| `v6_51.pdf` + `v6_51.pdf.ots` | the note `note/v6_51.pdf` exactly as in commit 6d42bb9 |

**Status: pending.** Created on 18 November 2026; not yet anchored in Bitcoin. A later commit will upgrade them.

How to verify: `pip install opentimestamps-client`, then `ots upgrade` and `ots verify` on each `.ots` (full
verification needs a Bitcoin node); `git rev-parse 6d42bb9 6d42bb9^{tree}` and `sha256sum timestamps/v2/v6_51.pdf`
to compare with `COMMIT.txt`.
