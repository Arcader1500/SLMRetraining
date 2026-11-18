# Frozen prepared datasets

Read the [dataset and cleaning guide](../docs/data/README.md) for preparation rules and limits.

| Folder / pointer | Category |
| --- | --- |
| `900825a06d38a006/`, `latest.json` | Historical v1, 1,325 train / 10 development |
| `eeff5efa1619f198/`, `latest_v2.json` | Historical full-schema v2, 1,325 / 30 |
| `e80798edebe5aba5/`, `latest_v3.json` | Current reduced-schema v3, 1,325 / 100 |

Each version owns its cleaned rows, tokenized data, manifests and cleaning/projection evidence. Keep these immutable; preparation changes belong in a new version. The separate `clinical_sft` CLI prepares an incompatible protocol under ignored `runs/`.
