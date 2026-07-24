# CYKG-Rec: Evidence-Graded Educational Knowledge Graph Recommendation

This repository contains the reproducible **code layer** for an evidence-graded educational knowledge graph and cross-subject recommendation prototype for Sichuan--Chongqing K--12 education.

It deliberately excludes textbooks, exercise books, OCR output, graph exports, model checkpoints, paper drafts, figures, experiment results, and other generated artifacts. These resources may have separate copyright, licensing, privacy, or provenance constraints and must not be uploaded with this repository.

## What is included

- Curriculum/content-unit graph construction, candidate concept retrieval, and candidate relation generation.
- Evidence-aware review-queue scoring and recommendation policy utilities.
- A lightweight EG-V3G-style graph-enhanced recommendation model, BKT baseline, and learner-path utilities.
- EdNet-KT2 public-data adapter and scripts for a learner-disjoint next-response protocol.
- Unit tests and an NVIDIA RTX A2000 8 GB-oriented example configuration.

## Important evidence boundary

Graph semantic edges produced by the code are **candidates**, not verified prerequisite relations. A model-generated audit is not a teacher/expert gold standard. The repository does not claim measured learning effects for Sichuan--Chongqing students. Any synthetic trajectory or ranking experiment must be labelled `synthetic-only`.

## Repository layout

```text
src/cykg_rec/        data, knowledge-graph, recommendation, model, and baseline code
experiments/          EdNet sample, split, and next-response scripts
configs/              example hardware/model settings
requirements/         pinned dependency groups
tests/                unit tests
```

## Environment

Python 3.11 is required. Create an isolated environment and install the editable package plus the CPU/data dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements/base.txt
```

For graph/transformer functionality, install the extra group after verifying PyTorch/CUDA compatibility:

```bash
python -m pip install -r requirements/kg_kt.txt
```

The supplied CUDA file targets PyTorch 2.0.1 with CUDA 11.7. Use it only when it matches your NVIDIA driver and hardware:

```bash
python -m pip install -r requirements/cuda117.txt
python experiments/smoke_test_cuda.py
```

The `configs/hardware_a2000_8gb.yaml` file is an example for an 8 GB GPU; reduce batch size or sequence length if an out-of-memory error occurs.

## Data preparation

No dataset is bundled. Place external data under ignored paths such as `data/raw/` and retain each source's original licence.

For the public EdNet-KT2 experiment, obtain the official EdNet-KT2 archives yourself and place them as:

```text
data/raw/interaction_logs/EdNet/EdNet-KT2.zip
data/raw/interaction_logs/EdNet/EdNet-Contents.zip
```

Then run the leakage-safe preparation pipeline:

```bash
python experiments/transform_ednet_kt2_sample.py --max-students 2000
python experiments/split_ednet_kt2_sample.py
python experiments/build_ednet_next_response_windows.py
```

This writes ignored Parquet files under `data/processed/interaction_logs/`. Learners are deterministically assigned to train/validation/test partitions, so do not reshuffle by event.

## Knowledge-graph pipeline

The modules below are intended to be invoked from your own pipeline configuration after placing licensed, traceable source material in `data/raw/` or `data/processed/`:

```text
cykg_rec.kg.extract_curriculum_seeds
cykg_rec.kg.build_content_graph
cykg_rec.kg.retrieve_concept_candidates
cykg_rec.kg.generate_prerequisite_candidates
cykg_rec.kg.score_review_queue
```

Keep provenance, page/segment identifiers, evidence types, confidence scores, and candidate-status fields in every generated record. Do not promote `candidate` relations to confirmed prerequisites solely from model output.

## Tests

Run the code-level test suite from the repository root:

```bash
python -m pytest -q
```

## Reproducibility notes

- Fix and report random seeds; preserve learner-disjoint splits.
- Report real public EdNet results, synthetic-only ranking results, and system/audit evidence separately.
- Do not commit raw educational content, student interaction logs, derived records, model checkpoints, or paper assets.
- Record package versions, GPU/device, and configuration files for every run.

## Licence

No open-source licence has been selected for this preliminary public code release. Before reuse or redistribution, please contact the repository owner. Third-party datasets and pretrained models are governed by their respective terms.
