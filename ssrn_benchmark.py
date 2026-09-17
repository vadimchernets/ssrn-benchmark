#!/usr/bin/env python3
"""
ssrn-benchmark — is your SSRN download count normal?

Since SSRN retired its public Rankings on 15 July 2026, authors see a raw
download counter with nothing to read it against. This tool supplies the
missing reference class, using an archival cross-section of 1,360 SSRN
papers whose counters were captured from the Internet Archive before the
sunset. That source is now closed: SSRN serves HTTP 403 to automated
clients, so this snapshot cannot be re-collected.

Usage
-----
    python3 ssrn_benchmark.py --downloads 29 --months 2
    python3 ssrn_benchmark.py --downloads 115 --months 2 --papers 4
    python3 ssrn_benchmark.py --table

Data: study1-wayback-downloads.csv (CC BY 4.0), DOI 10.5281/zenodo.22285871
No dependencies beyond the Python standard library.
"""
import argparse, bisect, csv, datetime as dt, os, statistics as st, sys

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study1-wayback-downloads.csv")
BANDS = [(0, 120, "under 4 months"), (120, 365, "4-12 months"), (365, 730, "1-2 years"),
         (730, 1825, "2-5 years"), (1825, 10**6, "over 5 years")]

def load():
    out = []
    with open(CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                pub = dt.datetime.strptime(r["pub_date"][:10], "%Y-%m-%d")
                snap = dt.datetime.strptime(r["snap_ts"][:8], "%Y%m%d")
                age, d = (snap - pub).days, int(r["downloads"])
            except (ValueError, KeyError):
                continue
            if age > 0:
                out.append((age, d, r.get("field", "")))
    if not out:
        sys.exit(f"No usable rows in {CSV}")
    return out

def band_for(days):
    for lo, hi, label in BANDS:
        if lo <= days < hi:
            return lo, hi, label
    return BANDS[-1]

def quantiles(sample):
    s = sorted(sample)
    q = lambda p: s[min(int(p * len(s)), len(s) - 1)]
    return dict(n=len(s), p25=q(.25), median=st.median(s), p75=q(.75), p90=q(.90), p95=q(.95))

def report(downloads, months, papers, recs):
    days = int(months * 30.44)
    lo, hi, label = band_for(days)
    peers = [d for a, d, _ in recs if lo <= a < hi]
    if len(peers) < 8:
        sys.exit(f"Too few comparable papers in the {label} band (n={len(peers)}).")
    per = downloads / papers if papers > 1 else downloads
    s = sorted(peers)
    pct = bisect.bisect_left(s, per) / len(s)
    q = quantiles(peers)

    print(f"\n  Your figure : {downloads:,} downloads" + (f" across {papers} papers = {per:,.0f} per paper" if papers > 1 else ""))
    print(f"  Paper age   : {months} months  ->  reference class \"{label}\" (n={q['n']})\n")
    print(f"  Percentile  : ~{pct:.0%}  (higher than {pct:.0%} of SSRN papers of the same age)\n")
    print(f"  That band   : 25%={q['p25']}   median={q['median']:.0f}   75%={q['p75']}   90%={q['p90']}   95%={q['p95']}")
    verdict = ("well above typical" if pct >= .80 else "above typical" if pct >= .60
               else "about typical" if pct >= .40 else "below typical" if pct >= .20 else "well below typical")
    print(f"  Verdict     : {verdict} for a paper of this age\n")
    print("  Read this carefully:")
    print("   - Download counters include automated traffic. COUNTER's June 2026 best")
    print("     practice requires excluding malicious bots and counting AI systems")
    print("     separately; raw platform counters do neither. Part of any count is not human.")
    print("   - The sample over-represents visible pages (a capture had to survive in the")
    print("     archive), so trust the SHAPE of the distribution, not absolute levels.")
    print("   - Downloads are not citations. The two are only weakly related.\n")

def table(recs):
    print("\n  SSRN lifetime downloads by paper age (n=1,360 archival cross-section)\n")
    print(f"  {'age band':<16}{'n':>6}{'25%':>8}{'median':>9}{'75%':>8}{'90%':>8}{'95%':>8}")
    print("  " + "-" * 63)
    for lo, hi, label in BANDS:
        peers = [d for a, d, _ in recs if lo <= a < hi]
        if len(peers) < 8:
            continue
        q = quantiles(peers)
        print(f"  {label:<16}{q['n']:>6}{q['p25']:>8}{q['median']:>9.0f}{q['p75']:>8}{q['p90']:>8}{q['p95']:>8}")
    print("\n  Note the 4-12 month band: counts do not climb steadily. Real growth")
    print("  starts after the first year, so a few months is too early to judge.\n")

def main():
    ap = argparse.ArgumentParser(description="Is your SSRN download count normal?")
    ap.add_argument("--downloads", type=int, help="your download count")
    ap.add_argument("--months", type=float, help="months since posting")
    ap.add_argument("--papers", type=int, default=1, help="if the count is a total across several papers")
    ap.add_argument("--table", action="store_true", help="print the full reference table")
    a = ap.parse_args()
    recs = load()
    if a.table or a.downloads is None:
        table(recs)
        if a.downloads is None and not a.table:
            ap.print_help()
        return
    if a.months is None:
        sys.exit("--months is required with --downloads")
    report(a.downloads, a.months, max(1, a.papers), recs)

if __name__ == "__main__":
    main()
