# Changes implemented over the MVP
### 11/16/2026
####  One part of patient isolation: protecting filesystem paths.
Now it:
- Accepts patient IDs such as `P001` and `john_doe`.
- Rejects IDs containing paths, such as `../other-folder`.
- Checks that the resolved patient directory (`medical-agent/data/patient_memory/P001`) stays inside the configured storage folder, and does not record outside patient storage (for example with `../other-folder`).
- Adds two tests covering valid and invalid IDs.

```bash
python -m unittest discover -s tests -v
```

#### PDF ownership
In v0, supplying a `pdf_id` skips the patient filter.