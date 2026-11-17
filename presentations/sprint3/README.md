# Sprint 3 presentation

- Google Slides deck (the live one): "Sprint 3 Slide Deck" in the BTE Capstone Drive folder, id `1YdcjysQXlJTmz-IwymgIBuPC0ltlp4hAPMTVNqiaGbM`.
- `Sprint3_Presentation_Firefly.pptx` and `source/build_sprint3.py`: the first build of the deck (Nov 17 snapshot). The Google Slides deck has moved on from it.
- `source/update_deck.py`: the daily refresh. It turns PostHog numbers into the charts on slides 4, 8 and 12, the data lines on slides 4, 5, 8, 9, 10 and 13, and the speaker notes on slides 4, 5, 8, 9 and 10.
- `data/state.json`: what the deck currently says. `data/summary.md`: the last update in plain English.

## What the numbers are

Totals = the shop's own log for Nov 12 to Nov 17 4:00 PM ET (fixed in `BASE` in the script, from the Google Form responses, before PostHog was switched on) + PostHog from Nov 17 4:00 PM ET onward. Team test visits (`is_test`) are excluded. Willingness to pay = checkout clicks by price shown. Customer acquisition = checkout clicks by channel (paid ads, Instagram organic, other).

## Daily refresh, step by step

1. Run this HogQL in PostHog (project 744620), with the PostHog connector's `execute-sql`:

```sql
SELECT price, channel, count() AS visitors, countIf(carts > 0) AS added_to_cart, countIf(checkouts > 0) AS clicked_checkout,
       sum(waitlist) AS waitlist_emails, countIf(expands > 0) AS opened_show_more
FROM (
  SELECT person_id,
         argMin(toString(properties.price), timestamp) AS price,
         argMin(multiIf(match(toString(properties.ad), '^[0-9]{10,}$'), 'paid',
                        toString(properties.src) IN ('ig_bio', 'ig', 'ig_story'), 'organic', 'other'), timestamp) AS channel,
         countIf(event = 'add_to_cart') AS carts, countIf(event = 'checkout') AS checkouts,
         countIf(event = 'notify') AS waitlist, countIf(event = 'description_expand') AS expands
  FROM events
  WHERE timestamp >= toDateTime('2026-11-17 21:00:00') AND timestamp < now()
    AND (properties.is_test IS NULL OR properties.is_test != true) AND properties.price IS NOT NULL
    AND event IN ('$pageview', 'add_to_cart', 'checkout', 'notify', 'description_expand')
  GROUP BY person_id)
GROUP BY price, channel ORDER BY price, channel LIMIT 100
```

2. Write the rows to `data/posthog.json` as `{"asof_label": "Nov 18, 10:47 PM", "range_end": "Nov 18", "rows": [[price, channel, visitors, added_to_cart, clicked_checkout, waitlist_emails, opened_show_more], ...]}` (New York time).
3. `python3 source/update_deck.py charts`, then commit and push, and note the commit SHA.
4. `python3 source/update_deck.py requests <SHA>` writes `data/requests.json` and prints the summary.
5. Read the deck's `revisionId`, then send `data/requests.json` to the deck with the Google Slides connector (`requiredRevisionId` set).
6. `python3 source/update_deck.py commit-state`, then commit and push.

If the summary has a "Needs a human read" section, the data now contradicts a conclusion on the slides; tell the team rather than rewriting the conclusions silently.
