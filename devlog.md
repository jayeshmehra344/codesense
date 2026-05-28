# codesense — Dev Log

---
2026-05-27
---

**Files modified today:**
- `src/data/github_loader.py` (15:25)
- `src/data/combine.py` (10:25)
- `data/training_data.json` (10:25)
- `data/combine.py` (09:58)
- `src/data/bugsinpy_loader.py` (09:24)

**Summary:**
Active day on the data pipeline — multiple loader scripts touched (GitHub, BugsinPy) and training data updated. The `combine.py` in both `src/data/` and `data/` were modified in the morning, suggesting work on merging/normalising data from multiple sources into a unified training set.

**Project structure snapshot:**
```
codesense/
├── src/
│   ├── api/          # empty — not yet built
│   ├── frontend/     # empty — not yet built
│   ├── data/
│   │   ├── github_loader.py      # fetches repos via GitHub API, stores in MongoDB
│   │   ├── bugsinpy_loader.py    # loads BugsinPy bug dataset
│   │   ├── cvefixes_loader.py    # loads CVEFixes vulnerability dataset
│   │   └── combine.py            # merges all data sources
│   ├── graph/
│   │   ├── pipeline.py           # clones repo → parses → saves graph to DB
│   │   ├── labeler.py            # labels graph nodes (buggy/clean)
│   │   └── db.py                 # MongoDB interface
│   ├── parser/
│   │   ├── parse.py              # AST parser — extracts functions & features
│   │   └── visualize.py         # graph visualisation (matplotlib)
│   └── model/
│       ├── gnn.py                # 3-layer GCN (CodeRiskGNN) — PyTorch Geometric
│       └── dataset.py            # PyTorch dataset wrapper
├── data/
│   ├── training_data.json        # compiled training set
│   ├── graph.json                # serialised graph
│   ├── cloned/                   # cloned repos (e.g. flask) for analysis
│   └── combine.py
├── tmp/
│   ├── bugsinpy/                 # BugsinPy raw data
│   └── github_repos/             # temp cloned repos during pipeline runs
├── notebooks/                    # empty
├── venv/                         # Python virtual environment
├── requirements.txt              # pinned deps (torch, torch-geometric, pymongo, etc.)
└── README.md                     # empty
```

**Current stage:**
Data collection and preprocessing is in active development. Three data sources are being wired together (GitHub API, BugsinPy, CVEFixes). The GNN model architecture (3-layer GCN for code risk classification) is defined but not yet trained. The graph construction pipeline is functional — it clones repos, parses ASTs, and stores structured graphs in MongoDB. API and frontend layers are stubbed but empty.

**Stack:** Python · PyTorch · PyTorch Geometric · MongoDB · NetworkX · HuggingFace Datasets

