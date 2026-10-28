# Sprint 2 presentations

Two decks built on the team's `Sprint2_Presentation_v4` template. They follow the Sprint 2 brief: intro, discovery to build, overview, demo, process, validation, summary, next steps. Each runs to five minutes, with timings in the speaker notes.

| Deck | Design |
|---|---|
| [`Sprint2_Presentation_Afterglow_Watch.pptx`](Sprint2_Presentation_Afterglow_Watch.pptx) | Afterglow watch: crown = I'm Home, pusher = SOS ([`afterglow-watch/`](../../afterglow-watch/)) |
| [`Sprint2_Presentation_Firefly_v2_Bracelet.pptx`](Sprint2_Presentation_Firefly_v2_Bracelet.pptx) | Firefly v2 bracelet: Button 1 = find / come find me, Button 2 = I'm home, both = SOS ([`v2-bracelet/`](../../v2-bracelet/)) |

Each deck embeds three videos (click to play in PowerPoint or Keynote):
- a 28-second cut of the promo film
- a recording of the app demo
- a recording of the website with a waitlist test sign-up. The recording intercepts the form post, so it doesn't add a row to the real Google Form.

There are also QR codes to the live site and app.

The "How We Tested" slide walks through the Firefly_User_Test study (consent, Task 1 find a friend, Task 2 night is over, survey) and what it measures.

**Before presenting, fill in:**
- the test numbers, the four stats (median find time, hints, clarity, usefulness) and the quote on "10 People Tried It", from the Firefly_User_Test CSV export
- the "Validated" line on "What We Learned"
- the number of waitlist sign-ups
- the 10 quotes in the appendix

If you import a deck into Google Slides, the embedded videos are dropped. Upload the files in `media/` to Drive and insert them from there.

`source/` holds the scripts that recorded the demos and built the decks.

## Google Slides editions

`google-slides/` holds a version of each deck made for Google Slides. When Google converts a .pptx, it drops embedded videos. In these editions, each video slide shows the poster frame with a ▶ badge instead.

To make the Google Slides copy:
1. Upload the file and the matching three MP4s from `media/` to the BTE Capstone Drive folder.
2. Open the .pptx with Google Slides, then choose **File → Save as Google Slides**.
3. On the film, app demo and website slides, choose **Insert → Video → Google Drive**, pick the matching MP4 and drag it over the poster.
