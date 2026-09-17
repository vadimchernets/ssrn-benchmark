# ssrn-benchmark — is your SSRN download count normal?

On 15 July 2026 SSRN retired its public Rankings. Authors kept the download
counter and lost everything to read it against. If your paper shows 7
downloads, nothing on the platform, and nothing in the literature, tells you
whether that is bad, ordinary, or good.

This tool answers that question.

```
$ python3 ssrn_benchmark.py --downloads 7 --months 2 --field "Social Sciences"

  Your figure : 7 downloads
  Paper age   : 2 months  ->  reference class "first year"
  Compared to : Social Sciences (n=24)

  Percentile  : ~25%  (higher than 25% of these papers)

  That band   : 25%=7   median=14   75%=30   90%=82   95%=86
  Verdict     : below typical for a paper of this age and field
```

No installation, no dependencies, no account. Python 3 and two files.

## The reference table

| Paper age | n | 25% | median | 75% | 90% | 95% |
|---|---|---|---|---|---|---|
| first year | 203 | 5 | 12 | 21 | 51 | 111 |
| 1–2 years | 253 | 15 | 25 | 44 | 108 | 165 |
| 2–5 years | 375 | 28 | 52 | 101 | 208 | 332 |
| 5–10 years | 188 | 72 | 130 | 376 | 914 | 1,358 |
| over 10 years | 341 | 96 | 172 | 336 | 851 | 1,441 |

**The median for a paper in its first year is 12** — far lower than most authors
assume. Counts keep accruing for decades rather than spiking and stopping.

Read the column downwards with care. The mix of fields in this sample changes
with age (Engineering is 24% of the young papers and 3% of the old ones), so
part of the rise down the column is composition rather than age.

## Field matters more than most authors expect

Among papers of the same age, median downloads differ by a factor of **4.7**
across subject fields:

| Field | n | median downloads, age 1–3 years |
|---|---|---|
| Business; Management and Accounting | 35 | 109 |
| Social Sciences | 61 | 71 |
| Economics; Econometrics and Finance | 53 | 65 |
| Computer Science | 34 | 46 |
| Agricultural and Biological Sciences | 23 | 29 |
| Environmental Science | 42 | 28 |
| Engineering | 132 | 25 |
| Materials Science | 39 | 23 |

A percentile computed without the field can therefore mislead by a wide margin.
Pass `--field` whenever you know it; `--fields` lists all 25.

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
- **Posting dates carry only a year.** 1,358 of the 1,360 records are stamped
  1 January, so there is no month in the data. Age is resolved to whole years and
  no shorter band is offered. An earlier version of this tool reported an "under
  4 months" band and a claim that counts do not climb steadily over the first
  year; both were artefacts of that stamp (72 of the 76 captures in that band fell
  in a single April) and have been withdrawn.
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
