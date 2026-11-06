"""Sanity-check the files produced by one agent run.

Usage:
    python evals/check_outputs.py                # checks ./outputs
    python evals/check_outputs.py --dir outputs --min-seconds 30 --max-seconds 600

Prints PASS/FAIL per check so you can copy the results into evals/results_template.csv.
Only the standard library is needed.
"""
import argparse
import wave
from pathlib import Path


def check(dir_: Path, min_s: float, max_s: float) -> bool:
    ok = True

    def report(name, passed, detail=""):
        nonlocal ok
        ok &= passed
        print(f"[{'PASS' if passed else 'FAIL'}] {name} {detail}")

    md = dir_ / "ai_research_report.md"
    report("report exists", md.exists())
    if md.exists():
        text = md.read_text(encoding="utf-8")
        report("report not empty", len(text.strip()) > 0, f"({len(text)} chars)")
        report("has 'Data Sourcing Notes' section", "Data Sourcing Notes" in text)

    wav = dir_ / "ai_today_podcast.wav"
    report("podcast audio exists", wav.exists())
    if wav.exists():
        try:
            with wave.open(str(wav)) as wf:
                secs = wf.getnframes() / wf.getframerate()
            report("audio duration in range", min_s <= secs <= max_s, f"({secs:.1f}s)")
        except wave.Error as e:
            report("audio is a valid WAV", False, f"({e})")

    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="outputs")
    ap.add_argument("--min-seconds", type=float, default=30)
    ap.add_argument("--max-seconds", type=float, default=600)
    a = ap.parse_args()
    raise SystemExit(0 if check(Path(a.dir), a.min_seconds, a.max_seconds) else 1)
