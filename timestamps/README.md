# OpenTimestamps proofs for commit 8a20bae

These files prove that the state of this repository at commit
`8a20baea52172b4e50b91b55a9c0452b757c1e08` existed at the time recorded by OpenTimestamps. Only hashes were sent to the
public calendars, never the content.

| file | what it attests |
|---|---|
| `COMMIT.txt` + `COMMIT.txt.ots` | the commit hash, its tree hash, and the SHA-256 of the note PDF and of the audit archive, as listed in `COMMIT.txt` |
| `v6_45.pdf` + `v6_45.pdf.ots` | the note exactly as in commit 8a20bae (a copy of `note/v6_45.pdf` from that commit) |
| `v6-45-audit-v5.zip` + `v6-45-audit-v5.zip.ots` | the audit archive, i.e. the `git archive` of commit 8a20bae |

**Status: pending.** The proofs were created on 15 November 2026 and are not yet anchored in Bitcoin. They will be
upgraded (`ots upgrade`) in a later commit.

## How to verify

```bash
pip install opentimestamps-client
ots verify timestamps/COMMIT.txt.ots          # also: v6_45.pdf.ots, v6-45-audit-v5.zip.ots
sha256sum timestamps/v6_45.pdf timestamps/v6-45-audit-v5.zip   # compare with COMMIT.txt
git rev-parse 8a20bae 8a20bae^{tree}                            # compare with COMMIT.txt
git show 8a20bae:note/v6_45.pdf | sha256sum                     # same hash as timestamps/v6_45.pdf
```

`ots verify` needs the proof to be upgraded and, for full verification, access to a Bitcoin node or block explorer.
