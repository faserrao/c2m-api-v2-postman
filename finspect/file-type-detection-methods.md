
# File Type Detection Methods — A Practical Guide

This document explains **all the common techniques** software uses to determine a file’s true type (e.g., PDF, RTF, TXT), including **how to inspect contents of ZIP archives**. It’s written for engineers implementing validation at an **API boundary** or building a **CLI**.

---

## Why file type detection matters

- **Security:** Prevent polyglot files, mismatched extensions, disguised executables, and decompression bombs.
- **Correct routing:** Choose the right parser/reader pipeline (PDF vs. image vs. plain text).
- **Compliance:** Enforce allow‑lists and content policies.
- **DX:** Provide clear error messages and telemetry when uploads don’t match expectations.

---

## Detection techniques (from weakest to strongest)

### 1) Filename extension (weak hint)
- Example: `.pdf`, `.rtf`, `.txt`.
- **Pros:** Free, instant.
- **Cons:** Trivially spoofed; often wrong; not authoritative.
- **Use it as:** A hint only, never a gate by itself.

### 2) Declared MIME type (client/transport hint)
- Source: HTTP headers like `Content-Type` (e.g., `application/pdf`), or multipart part headers.
- **Pros:** Easy to read; expresses client intent.
- **Cons:** Frequently inaccurate or generic (`application/octet-stream`); some clients lie or guess.
- **Best practice:** Record it, but independently verify via byte sniffing.

### 3) OS-level type systems (secondary hints)
- Windows **ProgID/registry**, macOS **UTI**, Linux **shared-mime-info** DBs.
- **Pros:** Integrates with platform conventions.
- **Cons:** Environment-dependent and still influenced by extension/associations.
- **Use it as:** A tie-breaker or UX improvement, not core validation.

### 4) Magic numbers / file signatures (authoritative core)
Inspect the first **few bytes** (“magic bytes”) to identify the format. This is how the Unix `file` utility and **libmagic** work.

**Common signatures**:

| Format | ASCII / Bytes | Hex (prefix) | Typical MIME |
|---|---|---|---|
| PDF | `%PDF-` | `25 50 44 46 2D` | `application/pdf` |
| RTF | `{\rtf` | `7B 5C 72 74 66` | `application/rtf` or `text/rtf` |
| PNG | `\x89PNG\r\n\x1A\n` | `89 50 4E 47 0D 0A 1A 0A` | `image/png` |
| JPEG | `\xFF\xD8\xFF` | `FF D8 FF` | `image/jpeg` |
| GIF | `GIF87a` / `GIF89a` | `47 49 46 38 37 61` / `47 49 46 38 39 61` | `image/gif` |
| ZIP | `PK\x03\x04` (local), `PK\x05\x06` (EOCD), `PK\x07\x08` (spanned) | `50 4B 03 04` etc. | `application/zip` |
| GZIP | `\x1F\x8B` | `1F 8B` | `application/gzip` |
| TAR | `ustar` at 0x101 | (tar header) | `application/x-tar` |
| MP3 | ID3 tag `ID3` or frame `FF FB` | `49 44 33` / `FF FB` | `audio/mpeg` |
| MP4 | `ftyp` box early | varies (`66 74 79 70`) | `video/mp4` |
| XML | starts with `<` and parses | (text) | `application/xml` |
| JSON | first non-ws `{` or `[` and parses | (text) | `application/json` |
| Plain text | high ratio of printable bytes, valid encoding | (text) | `text/plain` |

- **Pros:** Robust, fast, cross-platform.
- **Cons:** Some formats have ambiguous or missing signatures; polyglots exist.
- **Best practice:** Use **libmagic** (or equivalents) first; add custom rules as needed.

### 5) Structural / content sniffing (lightweight parsing)
Go beyond the first bytes; validate minimal structure:
- **JSON:** Trim whitespace; first char `{` or `[`; tiny parse with size/time limit.
- **XML/HTML:** Check for `<`, optional BOM; attempt minimal parse.
- **RTF:** Starts with `{\rtf`, optionally confirm closing brace balance (bounded scan).
- **Heuristic text vs. binary:** Printable‑byte ratio, null‑byte detection, BOM detection (UTF‑8/16/32).

**Pros:** Helps distinguish borderline cases (`.txt` vs `json`).  
**Cons:** Never do full parse at the boundary; keep time/size limits.

### 6) Container‑aware detection (ZIP, TAR, etc.)
Identify containers via magic bytes (e.g., ZIP: `PK..`). If container, you can **infer inner formats**:

- **OOXML** (`.docx/.xlsx/.pptx`): ZIP with `[Content_Types].xml` and folder structure:
  - `word/` → DOCX → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `xl/` → XLSX → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - `ppt/` → PPTX → `application/vnd.openxmlformats-officedocument.presentationml.presentation`
- **ODF** (`.odt/.ods/.odp`): ZIP with **root `mimetype` file** stored uncompressed that contains the exact media type (e.g., `application/vnd.oasis.opendocument.text`).

**Pros:** Precise for major office formats without full extraction.  
**Cons:** Requires reading central directory and a few inner files; watch for bombs.

### 7) Archive entry inspection (ZIP contents, without extracting)
When the top-level file is a ZIP and **policy allows**, iterate entries and sniff the first N bytes of each **uncompressed stream**:

- Use `zipfile` (Python) or equivalent API to open entries as streams.
- For each non-directory entry:
  - Read up to **N bytes** (e.g., 8192).
  - Apply magic/heuristics to determine MIME.
- Handle **encrypted entries** (report and optionally fail in `--strict` mode).
- **Ceilings:** max entries, max sniff bytes, total budget to avoid bombs.

**Pros:** Lets you enforce allow‑lists on embedded files.  
**Cons:** Needs strict resource limits to stay safe.

### 8) Library-based “meta” detection
- **libmagic** (`file` utility database): battle‑tested, wide coverage.  
- **Apache Tika:** parses and identifies thousands of types, understands containers; heavier runtime.  
- **Language libs:**  
  - Python: `python-magic`, `zipfile`  
  - Node: `file-type`, `mmmagic`, `yauzl`  
  - Go: `net/http.DetectContentType`, `zip`  
  - Rust: `infer`

**Pros:** Faster to implement, fewer false positives.  
**Cons:** Extra dependencies; must ship DBs/binaries in containers.

---

## Putting it all together: a robust detection pipeline

1. **Read a small prefix** of the file (4–16KB).  
2. **Try libmagic** (or equivalent). If present → primary result.  
3. If absent or uncertain → **magic‑byte table** + **light structural sniff**.  
4. If the top-level is a **container** (ZIP/TAR) and policy allows:
   - **Enumerate entries** (bounded by ceilings) and sniff each entry’s header bytes.
   - Apply **OOXML/ODF inference** for office docs.  
5. Produce a **media type**, **description**, and **confidence**, plus any **warnings** (encrypted, truncated, bomb‑like).  
6. Enforce an **allow‑list** and **mismatch policy** (e.g., reject if `Content-Type` header != sniffed type).

**ASCII flow**:

```
      ┌───────────┐
      │ read N KB │
      └─────┬─────┘
            v
     ┌───────────────┐  yes ┌─────────────┐
     │ libmagic ok?  ├─────►│ use result  │
     └──────┬────────┘      └────┬────────┘
            │ no                 │
            v                    v
   ┌────────────────┐    ┌──────────────────────┐
   │ magic signatures│    │ structural sniffing │
   └──────┬──────────┘    └──────────┬─────────┘
          │                          │
          └──────────────┬───────────┘
                         v
                ┌────────────────┐
                │ container? ZIP │
                └──────┬─────────┘
                       │ yes
                       v
            ┌────────────────────────┐
            │ list entries (bounded) │
            │ sniff each entry       │
            │ infer OOXML/ODF        │
            └─────────┬──────────────┘
                      v
               ┌────────────┐
               │ result +   │
               │ confidence │
               └────────────┘
```

---

## Example: API boundary pattern

### Python (FastAPI-style pseudocode)
```python
import magic

ALLOW = {"application/pdf", "text/plain", "application/zip"}

def detect_mime(buf: bytes) -> str:
    return magic.from_buffer(buf[:8192], mime=True)

async def upload(file):  # file is SpooledTemporaryFile or stream
    head = await file.read(8192); await file.seek(0)
    sniffed = detect_mime(head)
    declared = request.headers.get("Content-Type", "application/octet-stream")

    # log both for telemetry
    log.info({"declared": declared, "sniffed": sniffed})

    if sniffed not in ALLOW:
        raise HTTPException(415, f"Unsupported media type: {sniffed}")

    if declared != sniffed:
        # either reject, or normalize and continue
        log.warning("MIME mismatch", extra={"declared": declared, "sniffed": sniffed})

    # If ZIP, optionally inspect entries under ceilings before accepting
    return {"mediaType": sniffed}
```

### Node (Express-style pseudocode)
```js
import { fileTypeFromBuffer } from "file-type";

const ALLOW = new Set(["application/pdf","text/plain","application/zip"]);

app.post("/upload", async (req, res) => {
  const head = await peekBytes(req, 8192); // custom util that buffers N bytes
  const ft = await fileTypeFromBuffer(head);
  const sniffed = ft?.mime ?? "application/octet-stream";
  const declared = req.headers["content-type"] || "application/octet-stream";

  if (!ALLOW.has(sniffed)) return res.status(415).json({error: sniffed});
  if (declared !== sniffed) console.warn("MIME mismatch", {declared, sniffed});
  res.json({mediaType: sniffed});
});
```

---

## Resource ceilings & security notes

- **Zip bombs / decompression bombs:** cap entry count, per‑entry sniff bytes, total uncompressed budget.
- **Encrypted ZIPs:** report; optionally block unless explicitly permitted.
- **Time limits:** add soft timeouts to streaming reads.
- **Symlinks:** don’t follow by default; allow only with an explicit policy.
- **Never execute content:** treat uploads as untrusted; don’t shell out with file paths.
- **Max file size:** only read head bytes even for huge files; stream everything.

---

## Testing strategy (fixtures)

Create tiny fixtures and assert results:
- PDFs, images, text, JSON/XML, RTF.
- Valid DOCX/XLSX/PPTX (OOXML inference).
- ODT/ODS/ODP (root `mimetype` file).
- Mixed ZIP with a few file types.
- Encrypted ZIP (expect “encrypted” warning or strict failure).
- Truncated/corrupt ZIP.
- Empty file (expect `application/octet-stream` + warning).

---

## Reference libraries

- **libmagic** (`file` database): *gold standard* for byte‑signature detection.  
  - Python: `python-magic`  
  - Node: `mmmagic`, `file-type`  
  - Go: `net/http.DetectContentType` (basic), community libs for deeper coverage  
  - Rust: `infer`

- **Archive handling:** Python `zipfile`, Node `yauzl`/`yazl`, Go `archive/zip`.  

- **Deep/content analyzers:** **Apache Tika** (Java), great for broad coverage and containers.

---

## Appendix A — Extra magic byte examples

> All prefixes shown in hex (spaces optional). Only **peek** a small header; don’t load whole files.

- **BMP:** `42 4D`
- **WAV/AVI:** `52 49 46 46` (`RIFF`) + subtype later in header
- **FLAC:** `66 4C 61 43`
- **7z:** `37 7A BC AF 27 1C`
- **RAR:** `52 61 72 21 1A 07 00` (RAR 4) or `52 61 72 21 1A 07 01 00` (RAR 5)
- **ELF (Linux binary):** `7F 45 4C 46`
- **PE/EXE (Windows):** `4D 5A` (`MZ`)

---

## Appendix B — Confidence guidance

- **libmagic exact match:** 100  
- **Exact signature match:** 95–100  
- **Structural quick-parse success (JSON/XML/RTF):** 85–90  
- **Text heuristic:** 70–85  
- **Unknown/ambiguous:** 0 → `application/octet-stream`

---

## TL;DR (pocket checklist)

- Don’t trust **extensions** or **client headers** alone.  
- **Sniff bytes** (libmagic) and add **light structure checks**.  
- If **ZIP**, **enumerate entries** within resource ceilings; infer **OOXML/ODF**.  
- Enforce **allow‑lists**, log mismatches, and **fail safely**.
