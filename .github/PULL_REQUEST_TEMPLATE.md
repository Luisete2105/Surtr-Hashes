<!--
  Adding a new Surtr build hash? Fill in the fields below and add exactly one
  entry to hashes.json. See README.md for details.
-->

## Add a Surtr build hash

- **SHA-256:** `<the exact "Injecting Script SHA256" value>`
- **Surtr version:** `<e.g. 0.1.0>`
- **Nickname:** `<you>`
- **Name:** `<build name, e.g. "Luisete's Surtr">`
- **Date added:** `<YYYY-MM-DD>`
- **Note:** <what this build changes, e.g. "hud game as initial shared config">
- **Repo URL (optional):** <https://github.com/...>

### Checklist

- [ ] I copied the exact `Injecting Script SHA256` value printed by the injector.
- [ ] The hash is 64 lowercase hex characters.
- [ ] I added exactly one entry to `hashes.json`.
- [ ] `sha256`, `surtr_version`, `nickname`, `name` and `date_added` are filled in.
- [ ] Entries are ordered by Surtr version, then by date added.
- [ ] `python tools/validate_hashes.py` passes locally.
