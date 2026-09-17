# ssrn-benchmark — is your SSRN download count normal?

On 15 July 2026 SSRN retired its public Rankings. Authors kept the download
counter and lost everything to read it against. If your paper shows 7
downloads, nothing on the platform, and nothing in the literature, tells you
whether that is bad, ordinary, or good.

This tool answers that question.

```
$ python3 ssrn_benchmark.py --downloads 7 --months 2

  Your figure : 7 downloads
  Paper age   : 2 months  ->  reference class "under 4 months" (n=76)

  Percentile  : ~26%  (higher than 26% of SSRN papers of the same age)

  That band   : 25%=6   median=13   75%=18   90%=47   95%=55
  Verdict     : below typical for a paper of this age
```

No installation, no dependencies, no account. Python 3 and two files.

## The reference table

| Paper age | n | 25% | median | 75% | 90% | 95% |
|---|---|---|---|---|---|---|
| under 4 months | 76 | 6 | 13 | 18 | 47 | 55 |
| 4–12 months | 127 | 4 | 11 | 27 | 82 | 183 |
| 1–2 years | 252 | 15 | 25 | 44 | 108 | 165 |
| 2–5 years | 376 | 28 | 52 | 101 | 208 | 332 |
| over 5 years | 529 | 85 | 158 | 345 | 880 | 1,441 |

Two things worth noticing. **The median for a new paper is 13** — far lower
than most authors assume. And counts **do not climb steadily**: the 4–12 month
band sits no higher than the first four months. Real growth starts after the
first year, which is why a few months is too early to judge anything.

## Where the numbers come from

An archival cross-section of **1,360 SSRN papers**, published 1996–2026 across
25 fields. Their lifetime download and abstract-view counters were read from
Internet Archive captures, not from the live site.

**This snapshot cannot be re-collected.** SSRN now serves HTTP 403 to every
automated client, and the public Rankings that gave these counts their context
are gone. The window closed.

## Honest limits

- **The sample over-represents visible pages.** A paper had to have a surviving,
  parseable archive capture to be included. Trust the *shape* of the
  distribution, not platform-representative absolute levels.
- **Counters include machines.** COUNTER's *Best Practice on Generative and
  Agentic AI usage metrics* (30 June 2026) requires excluding malicious bots and
  counting AI systems separately. Raw platform counters do neither, so some
  share of any count is not a human reader.
- **Downloads are not citations.** They are only weakly related, and this tool
  says nothing about citation prospects.
- **Age is measured from a year-granularity posting date**, so ages inside the
  first year are approximate.

## Files

| File | |
|---|---|
| `ssrn_benchmark.py` | the tool, standard library only |
| `study1-wayback-downloads.csv` | the data, one row per paper (n=1,360) |

Columns: `aid` (SSRN abstract ID), `field` (OpenAlex field), `pub_date`,
`snap_ts` (archive capture), `downloads`, `abstract_views`.

## Citation

> Chernets, V. (2026). *An archival cross-section of SSRN download counts
> (n = 1,360)*. Zenodo. https://doi.org/10.5281/zenodo.22285871

The analysis behind it: *What Does 7 Downloads Mean? Metric Blindness and the
Cold Start of Scholarly Attention After the SSRN Rankings Sunset*,
https://doi.org/10.2139/ssrn.7296358

## Licence

Data CC BY 4.0 · code MIT.
