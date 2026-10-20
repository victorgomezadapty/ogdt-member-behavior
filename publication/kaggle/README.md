# OGDT Member Behavior · Kaggle package

Standalone notebook, source code only. No original data or individual exports are bundled.
`kernel-metadata.json` defaults to private, CPU, Internet enabled. The notebook downloads the
author's ZIP to temporary storage and verifies the archive/table hashes before any analysis.
It can alternatively read `OGDT_BERKELEY_ARCHIVE`. It does not depend on the repository layout,
precomputed reports or the sibling Retention lab. Only aggregates and an aggregate plot are written.

Build from the lab root: `python scripts/build_kaggle.py`.
Upload privately: `kaggle kernels push -p publication/kaggle`.
Check: `kaggle kernels status vctorandrsgmezlpez/ogdt-member-behavior-monthly-gym-attendance`.
Download execution outputs to an ignored local directory with `kaggle kernels output`.
The remote environment's actual Python/library versions are printed in the first code cell.
Kaggle provides numpy/pandas/matplotlib; the notebook does not install or modify dependencies.
The exact embedded source hashes are recorded in `build_manifest.json` and notebook metadata.

This is a **notebook publication**, not a new dataset publication. Underlying data rights are
not established by public download availability. See [source terms review](../../docs/publication_review.md).
The license for our original code does not license third-party source material or data.
Private validation is separate from making this notebook public.
