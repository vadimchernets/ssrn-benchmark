#!/usr/bin/env python3
"""
ssrn-benchmark — is your SSRN download count normal?

Since SSRN retired its public Rankings on 15 July 2026, authors see a raw
download counter with nothing to read it against. This tool supplies the
missing reference class, using an archival cross-section of 1,360 SSRN
papers whose counters were captured from the Internet Archive before the
sunset. That source is now closed: SSRN serves HTTP 403 to automated
clients, so this snapshot cannot be re-collected.

Field matters. Among papers of the same age, median downloads differ by a
factor of about 4.7 across subject fields, so a pooled percentile can be
misleading. Pass --field whenever you know it.

Usage
-----
    python3 ssrn_benchmark.py --downloads 29 --months 2 --field "Social Sciences"
    python3 ssrn_benchmark.py --downloads 115 --months 2 --papers 4
    python3 ssrn_benchmark.py --fields
    python3 ssrn_benchmark.py --table

Data: study1-wayback-downloads.csv (CC BY 4.0), DOI 10.5281/zenodo.22285871
No dependencies beyond the Python standard library.
"""
import argparse, bisect, csv, datetime as dt, os, statistics as st, sys

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study1-wayback-downloads.csv")
# Age is measured in WHOLE YEARS. 1,358 of the 1,360 posting dates in the sample
# carry the stamp 1 January, so the data has year resolution only and cannot
# support bands shorter than a year. An earlier version of this tool offered an
# "under 4 months" band; that band was an artefact of the stamp (72 of its 76
# captures fell in a single April) and has been withdrawn.
BANDS = [(0, 1, "first year"), (1, 2, "1-2 years"), (2, 5, "2-5 years"),
         (5, 10, "5-10 years"), (10, 10**6, "over 10 years")]
MIN_N = 8

def load():
    out = []
    with open(CSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                age = int(r["snap_ts"][:4]) - int(r["pub_date"][:4])
                d = int(r["downloads"])
            except (ValueError, KeyError):
                continue
            if age >= 0:
                out.append((age, d, r.get("field", "")))
    if not out:
        sys.exit(f"No usable rows in {CSV}")
    return out

def band_for(years):
    for lo, hi, label in BANDS:
        if lo <= years < hi:
            return lo, hi, label
    return BANDS[-1]

def quantiles(sample):
    s = sorted(sample)
    q = lambda p: s[min(int(p * len(s)), len(s) - 1)]
    return dict(n=len(s), p25=q(.25), median=st.median(s), p75=q(.75), p90=q(.90), p95=q(.95))

def resolve_field(name, recs):
    """Match a field name case-insensitively, by exact name or unique substring."""
    known = sorted({f for _, _, f in recs if f})
    exact = [f for f in known if f.lower() == name.lower()]
    if exact:
        return exact[0]
    hits = [f for f in known if name.lower() in f.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"Unknown field {name!r}. Run --fields to list the 25 available.")
    sys.exit("Ambiguous field {!r}; did you mean one of:\n  {}".format(name, "\n  ".join(hits)))

def verdict_for(pct):
    return ("well above typical" if pct >= .80 else "above typical" if pct >= .60
            else "about typical" if pct >= .40 else "below typical" if pct >= .20
            else "well below typical")

def report(downloads, months, papers, field, recs):
    years = int(months // 12)
    lo, hi, label = band_for(years)
    pooled = [d for a, d, _ in recs if lo <= a < hi]
    if len(pooled) < MIN_N:
        sys.exit(f"Too few comparable papers in the {label} band (n={len(pooled)}).")
    peers, scope = pooled, "all fields pooled"
    if field:
        in_field = [d for a, d, f in recs if lo <= a < hi and f == field]
        if len(in_field) >= MIN_N:
            peers, scope = in_field, field
        else:
            print(f"\n  Note: only {len(in_field)} papers in {field} within this age band,"
                  f" too few to condition on. Falling back to the pooled sample.")
    per = downloads / papers if papers > 1 else downloads
    s = sorted(peers)
    pct = bisect.bisect_left(s, per) / len(s)
    q = quantiles(peers)

    print(f"\n  Your figure : {downloads:,} downloads" + (f" across {papers} papers = {per:,.0f} per paper" if papers > 1 else ""))
    print(f"  Paper age   : {months:g} months  ->  reference class \"{label}\"")
    print(f"  Compared to : {scope} (n={q['n']})\n")
    print(f"  Percentile  : ~{pct:.0%}  (higher than {pct:.0%} of these papers)\n")
    print(f"  That band   : 25%={q['p25']}   median={q['median']:.0f}   75%={q['p75']}   90%={q['p90']}   95%={q['p95']}")
    print(f"  Verdict     : {verdict_for(pct)} for a paper of this age and field\n")

    if field and peers is not pooled:
        sp = sorted(pooled)
        pooled_pct = bisect.bisect_left(sp, per) / len(sp)
        if abs(pooled_pct - pct) >= .05:
            print(f"  Pooling across fields would have said ~{pooled_pct:.0%} instead of ~{pct:.0%}.")
            print(f"  Field median here is {q['median']:.0f} against {st.median(pooled):.0f} pooled.\n")
    elif not field:
        print("  No --field given, so this is a pooled percentile. Among papers of the same")
        print("  age, median downloads range from about 23 (Materials Science) to about 109")
        print("  (Business), a factor of 4.7, and the mix of fields shifts with age. Pass")
        print("  --field for a figure you can act on; --fields lists the 25 available.\n")

    print("  Read this carefully:")
    print("   - Download counters include automated traffic. COUNTER's June 2026 best")
    print("     practice requires excluding malicious bots and counting AI systems")
    print("     separately; raw platform counters do neither. Part of any count is not human.")
    print("   - The sample over-represents visible pages (a capture had to survive in the")
    print("     archive), so trust the SHAPE of the distribution, not absolute levels.")
    print("   - Posting dates carry only a year (1,358 of 1,360 are stamped 1 January),")
    print("     so age is resolved to whole years and no shorter band is offered.")
    print("   - Downloads are not citations. The two are only weakly related.\n")

def table(recs):
    print("\n  SSRN lifetime downloads by paper age (n=1,360 archival cross-section)\n")
    print(f"  {'age band':<16}{'n':>6}{'25%':>8}{'median':>9}{'75%':>8}{'90%':>8}{'95%':>8}")
    print("  " + "-" * 63)
    for lo, hi, label in BANDS:
        peers = [d for a, d, _ in recs if lo <= a < hi]
        if len(peers) < MIN_N:
            continue
        q = quantiles(peers)
        print(f"  {label:<16}{q['n']:>6}{q['p25']:>8}{q['median']:>9.0f}{q['p75']:>8}{q['p90']:>8}{q['p95']:>8}")
    print("\n  Age is in whole years: the posting dates carry no month.")
    print("\n  These rows pool all 25 fields. Because the mix of fields changes with age,")
    print("  the column read downwards overstates how much of the rise is age alone.\n")

def field_table(recs):
    """Median downloads by field, holding age roughly constant (1-3 years)."""
    lo, hi = 1, 4
    rows = {}
    for a, d, f in recs:
        if lo <= a < hi and f:
            rows.setdefault(f, []).append(d)
    rows = {f: v for f, v in rows.items() if len(v) >= 20}
    if not rows:
        sys.exit("Not enough data to break down by field.")
    print("\n  Median downloads by field, papers aged 1-3 years (n>=20 per field)\n")
    print(f"  {'field':<45}{'n':>6}{'median':>9}")
    print("  " + "-" * 60)
    for f, v in sorted(rows.items(), key=lambda kv: -st.median(kv[1])):
        print(f"  {f[:45]:<45}{len(v):>6}{st.median(v):>9.0f}")
    meds = [st.median(v) for v in rows.values()]
    print(f"\n  Spread at equal age: {min(meds):.0f} to {max(meds):.0f}, a factor of {max(meds)/min(meds):.1f}.")
    print("  This is why a pooled percentile can mislead.\n")

def list_fields(recs):
    known = sorted({f for _, _, f in recs if f})
    print(f"\n  {len(known)} fields in the sample:\n")
    for f in known:
        print(f"   {f}")
    print()

def main():
    ap = argparse.ArgumentParser(description="Is your SSRN download count normal?")
    ap.add_argument("--downloads", type=int, help="your download count")
    ap.add_argument("--months", type=float, help="months since posting (resolved to whole years)")
    ap.add_argument("--papers", type=int, default=1, help="if the count is a total across several papers")
    ap.add_argument("--field", help="your subject field, for a like-for-like comparison")
    ap.add_argument("--table", action="store_true", help="print the reference table by age")
    ap.add_argument("--field-table", action="store_true", help="print median downloads by field at equal age")
    ap.add_argument("--fields", action="store_true", help="list the available field names")
    a = ap.parse_args()
    recs = load()
    if a.fields:
        return list_fields(recs)
    if a.field_table:
        return field_table(recs)
    if a.table or a.downloads is None:
        table(recs)
        if a.downloads is None and not a.table:
            ap.print_help()
        return
    if a.months is None:
        sys.exit("--months is required with --downloads")
    field = resolve_field(a.field, recs) if a.field else None
    report(a.downloads, a.months, max(1, a.papers), field, recs)

if __name__ == "__main__":
    main()
