# Workshop 02 · Context & memory

Open **learner-worksheet.html** in any current browser. It works offline and saves a `decision.md` you can use for the debrief. This is the shared path for the live workshop.

If you already have Python 3.10 or later, open a terminal in this folder. The starter uses only the standard library. It requires no API key, server, package install, or data download.

## Lab A · Retrieval

```bash
python3 retrieval.py control static
python3 retrieval.py join static
python3 retrieval.py join static --k 4
python3 retrieval.py join dynamic
python3 retrieval.py join programmatic
```

Read the `trace`, `answer`, and `stop_reason` fields. Both retrieval routes start with the same two test accounts, query, and top two records. This isolates the effect of the second lookup. The dynamic route can follow a missing deal status into a batched CRM lookup. The programmatic route uses a direct filter and join. The hybrid ranker combines BM25 with a small authored concept vocabulary through reciprocal rank fusion. The numbers under `local_ms` measure local code. `cost` estimates what the route hands a model to read: tokens at four characters each, dollars at `--price-per-mtok` (default: the Sonnet 5.5 input list price), and `full_corpus_tokens_est` for the whole corpus in one prompt. `model_reads` counts the model calls; the dynamic route reads twice when the first pass leaves a gap. All records are synthetic.

With `--k 4` the first pass returns the two emails before either CRM row. Work out why before the debrief: the CRM rows share no word with the query, the emails match the stopwords “a” and “and” in the BM25 channel, and the fusion step rewards a record that appears in both channels. That is a retrieval-tuning problem, and it is also why a lookup by account ID beats a wider search here.

### Extension · a corpus too big to read

`records-large.json` has 400 accounts and about 1,000 records. The `discover` question has to find its own candidates, and `coverage` compares what each route supported with the answer the corpus itself gives.

```bash
python3 retrieval.py discover static --corpus records-large.json --k 10 --brief
python3 retrieval.py discover dynamic --corpus records-large.json --k 30 --brief
python3 retrieval.py discover programmatic --corpus records-large.json --brief
```

Read `coverage.recall` and `coverage.missed`. Change `--k` and watch recall move. The corpus still fits a model’s context window; what it no longer fits is a person reading it during the session.

Then read `cost`. Per answer the static route is the cheapest and supports nothing. The programmatic route reads about 5,400 tokens and supports all 32 accounts, so per supported account it costs about half of the dynamic route at `--k 30`. The whole corpus in one prompt is about 46,600 tokens, nearly nine times the programmatic route. On the 12-record fixture the whole corpus is 530 tokens and the choice of route is worth nothing. That is the crossover the homework card asks you to find: the corpus size at which code over the data becomes the cheapest route per supported account. The recorded RLM run on slide 10 over this same corpus is the third point: two model calls, 8,084 input and 1,609 output tokens measured, all 32 accounts supported, about five cents at list price. The RLM costs more than the fixed code because the model writes the code each time; that is the price of a question that changes.

## Lab B · Run a dreaming pass, then make the write guard hold

The synthetic archive has 32 historical transcripts across eight topics and four new transcripts in `lab-b/client-a/incoming.md`. The Client A starter wiki is in `lab-b/client-a/wiki/`. Client B has a separate published wiki.

Open the extracted folder in your coding agent and give it this request:

> Read `memory-wiki/SKILL.md` and run one manual dreaming pass for Client A. Use `lab-b/client-a/wiki/` and `lab-b/client-a/incoming.md`. Check `lab-b/client-a/history/` for supporting sources as needed. Propose a diff outside the published wiki. Cite the source and authority for each proposed change and suggest links between related topics. Wait for my review.

Review the diff. Your agent will probably propose more hunks than the instructor’s worked example and may add no new pages; approve each hunk on its source and authority. Ask the agent to save a copy of the original wiki as the baseline, apply the changes you approve, and generate the map:

```bash
python3 memory-wiki/wiki_map.py lab-b/client-a/wiki
```

Open the resulting `wiki-map.html` and follow one link. For the fresh-session test, ask your agent to copy only the Markdown pages of the baseline and the updated wiki into two separate folders outside the extracted starter. Give each folder to a new reader session. Ask each, “Use the wiki in this folder. Who should Client A contact first? Which file did you open and what is your source?” Ask the updated reader what the wiki establishes about the discount. Record the answers and the files each reader actually used.

If time is short, read the baseline page yourself and test the updated reader. In the live lab, record how you would test Client B in the worksheet. For an extra run, start another session with only Client B’s Markdown wiki.

### The write guard

The review above depends on a reader. The second gate lives in the application. `memory.py` is a small store with its own sources in `memory.json`; it is a separate system from the wiki. The starter ships with the two hooks open and four failing checks:

```bash
python3 -m unittest -v checks
python3 memory.py client-b
```

The four failures are the planted problems: a call note that approves a discount, a correction whose value or client changes on the way in, Client A rows visible to Client B, and expired or superseded rows that still load. Work on `allow_write` and `visible` in `memory.py` (the two edit points) until all four checks pass without touching `checks.py` or `memory.json`. The source `kind`, the client scope, the effective and expiry dates and `superseded_by` are what you have to work with. Then run `python3 memory.py client-b` again: it should return only OWNER-12. If time runs out, the instructor shows a reference guard passing the same checks, and finishing is a homework extension.

If you use the worksheet alone, read the evidence excerpts, write the diff you would approve, and predict the next session’s answer. The instructor will show a worked wiki and the guard checks during the reveal.

## Homework · due before the 22 November session

Required: one `decision.md` from your own workflow, Track A or Track B. The question, the evidence you had, the lookup or memory change you made, and what a fresh session answered before and after. Label the evidence mode. Keep it within the course’s homework budget of 3-4 hours.

Extension cards: run the `discover` route on the extension corpus and report recall and cost per answer at two values of `k`, for the retrieval routes and for the programmatic route (compare `cost.usd_per_supported_include_est`); make the four memory checks pass if you did not finish in the session; run the memory wiki skill on one recurring question in your own project.

## Apply it to your own agent

Give [the memory wiki skill](memory-wiki/SKILL.md) to your coding agent and point it at one recurring question and a few approved sources. You can paste the file into any agent that can work with your project files. The first run builds a small wiki, proposes one manual update, and checks whether a fresh session can use it.
