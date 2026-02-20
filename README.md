# edgebench ⚡

> Community-driven local LLM inference benchmarks across real hardware.

**edgebench** is a CLI tool that benchmarks local LLM inference on your hardware and lets you contribute results to a shared community database. The goal is to answer the question developers constantly ask: *"Will this model run fast enough on my hardware?"*

---

## Why this exists

There's no centralized, reproducible database of local LLM performance across real consumer hardware. edgebench fixes that by making it dead simple to run a standardized benchmark and share your results.

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/BRDY-SCAG/edgebench
cd edgebench
pip install -r requirements.txt

# 2. Make sure Ollama is running with a model pulled
ollama pull llama3.2:3b

# 3. Run the benchmark
python cli/main.py run --model llama3.2:3b --runs 3
```

---

## What it measures

- **Tokens per second** (avg, min, max, stdev)
- **Time to first token** (TTFT)
- **Total inference time**

Across 3 standardized prompt categories: factual, reasoning, and creative.

---

## Contributing your results

Coming soon — a `submit` command that opens a PR to this repo with your result JSON.

For now, feel free to manually open a PR adding your result file to `submissions/`.

---

## Roadmap

- [x] Ollama backend
- [x] MLX backend (Apple Silicon)
- [ ] llama.cpp direct backend
- [ ] `edgebench submit` command (auto PR to this repo)
- [ ] Auto-generated community dashboard
- [ ] C++ native profiler module for precise memory tracking
- [ ] Rust rewrite of core measurement engine

---

## Hardware tested so far

<!-- DASHBOARD_START -->
| Hardware | Model | Avg tok/s | TTFT (ms) | OS | Submitted by |
|---|---|---|---|---|---|
| Apple M3 Pro (18.0GB unified) | llama3.2:3b | 61.59 | 65.5 | Darwin 25.3.0 | BRDY-SCAG |
| Apple M3 Pro (18.0GB unified) | mlx-community/Llama-3.2-3B-Instruct-4bit | 72.21 | 0.0 | Darwin 25.3.0 | BRDY-SCAG |
<!-- DASHBOARD_END -->

---

## Project structure

```
edgebench/
├── cli/              # Entry point
├── backends/         # Inference backend wrappers
├── core/             # Benchmark runner, hardware detection, reporter
├── results/          # Your local results (gitignored)
├── submissions/      # Community results (PRs welcome!)
└── requirements.txt
```

---

## License

MIT
