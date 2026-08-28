#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""How long the editor waits for diagnostics.

A language server is not measured in throughput. It is measured against a
person typing. The client recomputes diagnostics on every change, so what
matters is a single question: **does the answer come back before the user
notices?**

Two thresholds are worth naming, and the table marks both:

* **~16 ms** — one frame. Under this, diagnostics feel instantaneous;
  squiggles move with the cursor.
* **~100 ms** — the limit of "the system is reacting instantly". Past it
  the editor feels laggy on every keystroke, and past a few hundred
  milliseconds people start turning the extension off.

Measured across document sizes, because a MT940 statement document is not one
entry — a real one is hundreds, and the file only ever grows while
somebody is editing it.

Also measured: **completion and hover**, which are called on demand rather
than on every change but block the UI while they run, and the **malformed
path**, which is the state a document spends most of its life in while
being typed. A linter that is fast on valid input and slow on invalid
input is slow exactly when the editor calls it most.

Run::

    python benches/bench_diagnostics.py
    python benches/bench_diagnostics.py --json
    python benches/bench_diagnostics.py --quick     # what CI runs

Nothing here asserts a threshold: wall-clock is not comparable between
machines, and a flaky performance gate teaches people to ignore red. CI
runs ``--quick`` so a benchmark that has stopped compiling against the
current API fails the build instead of rotting into a file that reads as
verified and is not.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bankstatementparser_lsp.diagnostics import (  # noqa: E402
    diagnostics_for_mt940,
)

FRAME_MS = 16.0
INSTANT_MS = 100.0

_HEAD = """:20:STMT-BENCH
:25:COBADEFFXXX/DE89370400440532013000
:28C:42/1
:60F:C260620EUR1000,00
"""

_ENTRY = """:61:2606210621CR{amount},00NMSCREF{i}//CREF{i}
:86:Benchmark entry {i}
"""

_TAIL = ":62F:C260621EUR2000,00\n"


def build(entries: int) -> str:
    """An MT940 statement carrying ``entries`` transaction lines."""
    body = "".join(
        _ENTRY.format(amount=(i % 900) + 100, i=i) for i in range(entries)
    )
    return _HEAD + body + _TAIL


def corrupt(text: str) -> str:
    """The same statement mid-edit: a balance line half typed."""
    return text.replace(":60F:C260620EUR1000,00", ":60F:C2606", 1)


def diagnose(text: str) -> list:
    return diagnostics_for_mt940(text)


# This server offers diagnostics only -- no completion or hover -- so
# there is nothing on-demand to measure. An empty list is the honest
# answer; inventing a row would imply a feature that does not exist.
ON_DEMAND: list = []


def _best(call, repeats: int) -> float:
    """Best-of timing after one untimed warm-up.

    The minimum is the least noisy estimator here; the mean follows
    whatever else the machine is doing. A language server's worst case
    matters too, but the floor is what tells you whether the design can be
    responsive at all.
    """
    call()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        samples.append(time.perf_counter() - start)
    return min(samples)


def _verdict(ms: float) -> str:
    if ms <= FRAME_MS:
        return "instant"
    if ms <= INSTANT_MS:
        return "fine"
    return "LAGGY"


def measure(size: int, repeats: int) -> dict:
    valid = build(size)
    broken = corrupt(valid)
    good = _best(lambda: diagnose(valid), repeats)
    bad = _best(lambda: diagnose(broken), repeats)
    return {
        "size": size,
        "bytes": len(valid),
        "valid_ms": good * 1e3,
        "malformed_ms": bad * 1e3,
        "verdict": _verdict(good * 1e3),
    }


def run(quick: bool) -> dict:
    sizes = [1, 25] if quick else [1, 25, 100, 500]
    repeats = 3 if quick else 7
    rows = [measure(n, repeats) for n in sizes]
    ondemand = []
    for name, call in ON_DEMAND:
        ondemand.append({"call": name, "ms": _best(call, repeats) * 1e3})
    return {"diagnostics": rows, "on_demand": ondemand}


def render(results: dict) -> None:
    print("diagnostics — what the editor waits for on every keystroke")
    print(
        f"{'entries':>10}{'KiB':>8}{'valid ms':>10}"
        f"{'malformed ms':>14}{'verdict':>10}"
    )
    for row in results["diagnostics"]:
        print(
            f"{row['size']:>10}{row['bytes'] / 1024:>8.1f}"
            f"{row['valid_ms']:>10.2f}{row['malformed_ms']:>14.2f}"
            f"{row['verdict']:>10}"
        )
    print(
        f"\n  instant = under {FRAME_MS:.0f} ms (one frame), "
        f"fine = under {INSTANT_MS:.0f} ms, LAGGY above it.\n"
        "  The malformed column is the state a document spends most of its\n"
        "  life in while somebody is typing. If it is much slower than the\n"
        "  valid column, the linter is slowest exactly when the editor\n"
        "  calls it most."
    )
    rows = results["diagnostics"]
    largest = rows[-1]
    if largest["size"] and largest["valid_ms"]:
        per = largest["valid_ms"] / largest["size"]
        budget = int(INSTANT_MS / per) if per else 0
        # Two decimals renders a fast server as "0.00 ms", which reads as
        # a broken measurement rather than a good result.
        shown = f"{per:.2f}" if per >= 0.01 else f"{per:.4f}"
        print(
            f"\n  Cost is about {shown} ms per entry, so the editor "
            f"stops feeling instant at roughly **{budget} entries** and "
            f"stops feeling attached to the keyboard well before that.\n"
            f"  That number is the one to watch: it is a budget, not a "
            f"score, and it tells you the document size this server is "
            f"actually usable on."
        )
    if largest["valid_ms"] > INSTANT_MS:
        print(
            f"\n  At {largest['size']} the editor waits "
            f"{largest['valid_ms']:.0f} ms per change."
        )

    print("\non demand — called by a keystroke, but not by every keystroke")
    print(f"{'call':>18}{'ms':>10}{'verdict':>10}")
    for row in results["on_demand"]:
        print(f"{row['call']:>18}{row['ms']:>10.3f}{_verdict(row['ms']):>10}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--quick", action="store_true", help="small sizes, as CI runs"
    )
    args = parser.parse_args()

    results = run(quick=args.quick)
    if args.json:
        json.dump(results, sys.stdout, indent=1)
        print()
    else:
        render(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
