# Benchmarks

`benches/bench_diagnostics.py` measures what an editor waits for on every
keystroke: one call to `diagnostics_for_mt940` on a whole MT940 document,
for valid documents and for malformed ones (the state a document spends
most of its life in while being typed), across document sizes. The
verdict column marks the two thresholds that matter: under 16 ms (one
frame) feels instant, under 100 ms still feels attached to the keyboard.

Nothing asserts a threshold: wall-clock is not comparable between
machines. CI runs `python benches/bench_diagnostics.py --quick` on every
push so the benchmark keeps running against the current API.

## Results

Run with `poetry run python benches/bench_diagnostics.py` on
2026-11-27: Apple M1 Pro, macOS 27.2.1, CPython 3.12.16,
bankstatementparser-lsp 0.0.36.

| Entries | KiB | Valid ms | Malformed ms | Verdict |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 0.2 | 0.00 | 0.01 | instant |
| 25 | 1.6 | 0.03 | 0.03 | instant |
| 100 | 6.2 | 0.12 | 0.12 | instant |
| 500 | 32.0 | 0.56 | 0.56 | instant |

Cost grows linearly at about 0.0011 ms per entry on this machine, and
malformed documents cost the same as valid ones, so the linter is not
slower when the editor calls it most. At that rate a document would need
roughly 89,000 entries before diagnostics took longer than one frame.

Reproduce with `python benches/bench_diagnostics.py` (add `--json` for
machine-readable output).
