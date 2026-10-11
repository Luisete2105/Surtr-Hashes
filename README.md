# Surtr Hashes

A public registry of known Surtr build hashes, used to verify that a run was
played on a released version of Surtr or an approved community fork.

The `t7-compiler` injector prints the SHA-256 of the compiled Surtr file it
injects:

```
Injecting Script SHA256: 9f2a…c7
```

That value is the **build hash**. When you fork Surtr and change something (for
example `initial_config.gsc`), recompiling produces a different hash. Add it
here so verifiers can look it up.

## Verify a hash

Open the hosted page (GitHub Pages) and either:

1. Type or paste a hash — results update live as you type, showing every
   registered build whose hash contains the exact characters entered (a partial
   hash matches any build it appears in). A full 64-character hash gives the
   exact build.
2. Choose the compiled Surtr file and let the page compute its SHA-256 and look
   it up.

It will tell you which build the hash belongs to, or that it is unknown.

## Files

| File | Purpose |
|------|---------|
| `hashes.json` | The registry (single source of truth). |
| `index.html` | The verifier page, which can also create/edit entries and export the registry. |
| `tools/validate_hashes.py` | Validates `hashes.json` (also run by CI). |
| `.github/` | PR template and the validation workflow. |

### Where the page loads its data

`index.html` fetches its registry from the `REGISTRY_URLS` list at the top of
its `<script>` (currently `./hashes.json`). Since the page and `hashes.json` live
in the same repo, that relative path already points at the uploaded file on
GitHub Pages — no change needed there. To also let the page run from another
location, add the raw link as a fallback entry in that list:

```js
var REGISTRY_URLS = [
  "./hashes.json",
  "https://raw.githubusercontent.com/<user>/surtr-hashes/main/hashes.json"
];
```

Each URL is tried in order until one loads.

Opening `index.html` straight from disk (`file://`) fails with a
`NetworkError` because browsers block `fetch` for local files. Use the hosted
page, or click **Load file…** to pick `hashes.json` manually.

## Entry format

```json
{
  "schema": 1,
  "entries": [
    {
      "sha256": "9f2a…c7",
      "surtr_version": "0.1.0",
      "nickname": "luisete2105",
      "name": "Luisete's Surtr",
      "note": "Has `hud game` as the initial shared config and `autosplit` as the initial zm config.",
      "repo_url": "https://github.com/…",
      "date_added": "2026-10-11",
      "approved_by": ["luisete2105", "another_reviewer"]
    }
  ]
}
```

### Fields

| Field | Required | Description |
|-------|:--------:|-------------|
| `sha256` | yes | SHA-256 of the compiled Surtr file (64 lowercase hex chars). |
| `surtr_version` | yes | Base Surtr version this build is based on (e.g. `0.1.0`). |
| `nickname` | yes | Who made the build. |
| `name` | yes | Display name of the build. |
| `note` | no | What this build changes compared to the base version. |
| `repo_url` | no | Link to the fork's repository. |
| `date_added` | yes | Date the entry was added (`YYYY-MM-DD`). |
| `approved_by` | no | Reviewer name(s) who approved the entry. Can be one name, a list of names, or `""` (empty) / omitted when nobody has verified it yet. |

### Ordering

Entries are ordered by `surtr_version` (real version order, so `0.1.0` before
`0.1.1` before `0.10.0`), then by `date_added` (oldest first). The verifier page
re-sorts on load, but keep the file itself ordered so diffs stay clean.

## Editing the registry with the page

The page can build entries for you:

- **Verify a hash** — type a hash to see matches live, or choose the compiled
  Surtr file to have its SHA-256 computed and looked up.
- **+ New entry** — fill in the fields (the date defaults to today). For
  `approved_by`, add each reviewer as a chip (multiple are allowed). You can
  paste the hash or use "Use file…" to compute it from the compiled file.
- **Edit / Delete** — change a note, add an approver, fix a field, or remove an
  entry directly in the table.
- **Load file…** — import an existing `hashes.json` to edit offline.
- **Download hashes.json / Copy JSON** — export the result.

The page is static, so it cannot commit for you: export the file and open a pull
request with it.

## Submitting a hash

1. Fork this repository.
2. Add one entry to the `entries` array in `hashes.json`, keeping it ordered.
3. Run `python tools/validate_hashes.py` and make sure it passes.
4. Open a pull request and fill in the template.

Every pull request is reviewed and merged manually, so nothing is added without
approval.

## License

MIT — see [LICENSE](LICENSE). The data in `hashes.json` may only contain build
hashes and descriptive metadata, never the compiled files themselves.
