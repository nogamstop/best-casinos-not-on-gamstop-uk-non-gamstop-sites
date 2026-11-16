# November update — structural QA

{
  "date": "2026-11-16",
  "author": "Casino Notes Editorial Team",
  "reviewBodyWordCounts": {
    "Donbet": 498,
    "Goldenbet": 498,
    "Betportal": 504,
    "MyStake": 499,
    "Wildies": 506,
    "Betride": 496,
    "CasinoK": 506,
    "BetFoxx": 503,
    "Booming Slots": 504,
    "Patrick Spins": 503
  },
  "totalReviewBodyWords": 5017,
  "cards": 10,
  "logos": 10,
  "affiliateLinks": 10,
  "duplicateIds": 0,
  "brokenInternalLinks": 0,
  "htmlSha256": "ba82f1f901de06cc40e3a4212102119f9933d33659ec87ede8594c3b4191df21",
  "originalCoreCssPreserved": true,
  "browserChecks": "Not yet run by this build script."
}

Word counts cover review body paragraphs, excluding headings, cards and source lists. Checks above were executed by the build script. Browser checks, when run, are recorded separately below. The earlier report below describes the previous design, not a new run against this update.

# QA — approved single-page design v2

## British English documentation and Pages preparation — 16 November 2026

- Reviewed `README.md`, `CHANGELOG.md` and this QA record. Replaced the Bulgarian README with British English and standardised the documentation wording.
- Confirmed the approved HTML declares `<html lang="en-GB">`.
- Scanned the matching local HTML for Cyrillic characters; none were found.
- Recalculated the local HTML's file size, Git blob SHA and SHA-256. They match the recorded approved values below. The repository tree also reports the same HTML blob SHA.
- Kept `index.html` unchanged. Programming keywords and CSS values such as `color` and `center` are identifiers, not public-facing spelling errors.
- Confirmed `.nojekyll` is present in the repository and recorded branch-based publishing instructions in the README.

At the repository-settings check, `has_pages` was `false`. These documentation changes do not enable GitHub Pages. No live deployment or additional browser test run is claimed for this update.

## GitHub upload verification — 16 November 2026

The HTML in `github-upload-ready.zip` matched the approved local `casino-affiliate-v2.html` exactly before upload. The file was uploaded as root-level `index.html` on `main`.

GitHub returned the same content-addressed blob identifier as the locally calculated value:

```text
File size:     107154 bytes
Git blob SHA:  44f75fcb3a4980abab086772643601a03c73fce1
SHA-256:       98b93d66c4eaee414218ea4dc1ad2aff28627c53500eca31eb7d3d994657beca
```

The upload-stage local structural inspection found:

- One H1, containing the approved title.
- No duplicate IDs.
- No broken internal anchor targets.
- No remote script, stylesheet or image dependencies in the page.
- No matches in a limited scan for common GitHub tokens, AWS access-key identifiers or private-key headers. This is not a comprehensive security audit.

Hosting and a public website deployment were not configured or tested during this upload. PNG preview files are not included in the repository and are not runtime dependencies.

## Recorded design QA from the approved package

The following results are retained from the earlier v2 design QA report. The full browser matrix was not rerun during the upload or documentation update; content integrity was checked as described above.

### Environment and scope

Tested in headless Chromium using Playwright. The generated HTML was loaded directly into the browser for testing, without a public deployment. These are browser-emulation and functional checks, not tests on physical phones, Safari or Firefox.

### Responsive layout

Tested viewport widths: 320, 360, 390, 430, 590, 768, 780, 820, 1000, 1024, 1280, 1440 and 1920 pixels.

No document-level horizontal overflow was found at the tested widths. The section navigation intentionally scrolls horizontally on narrow screens. The comparison table scrolls inside its dialogue box on small screens.

Visual inspection included the desktop and mobile first screens and the long-form article layout.

### Functional checks

- PASS: Research-status filter shows the correct two cards.
- PASS: Name search combines correctly with an active filter.
- PASS: Zero-result state and reset return all four cards.
- PASS: Alphabetical sorting works in both directions.
- PASS: Two-site comparison, table, Escape dismissal and body scrolling work.
- PASS: Three-site limit, warning, comparison and clear control work.
- PASS: Review buttons and source links open their collapsed sections.
- PASS: Direct deep links reveal the requested review note.
- PASS: Editorial disclosure dialogue box and navigation work.
- PASS: FAQ accordion opens.
- PASS: Mobile menu expands and closes after navigation.
- PASS: No-JavaScript fallback retains all cards, text and expandable notes.

### Structural checks

- One H1.
- Four casino cards and eight FAQ disclosures.
- No duplicate IDs.
- All in-page anchor targets exist.
- JavaScript syntax check passed.
- No browser JavaScript errors in the recorded run.
- No remote font, image, script or stylesheet dependencies.

## Not verified by these checks

Operator facts, live bonuses, withdrawal performance, launch dates, licensing status of individual casinos, affiliate conversion performance, third-party destinations and a public deployment were not tested by the UI checks. This is not a full accessibility audit or cross-browser certification.


## Executed browser checks for the November update

{
  "engine": "Headless Chromium / Playwright 1.56.0",
  "checks": [
    "Ten cards, ten reviews, ten decoded supplied logos and the requested byline.",
    "Status filters, combined search, no-result state and reset.",
    "Alphabetical sorting and restoration of the publisher-selected order.",
    "Three-site comparison limit, populated comparison table and Escape dismissal.",
    "Internal full-review navigation, source disclosure and FAQ.",
    "No document-level horizontal overflow at 320, 360, 390, 590, 768, 1000 and 1440 pixels.",
    "Mobile navigation opens and closes after choosing a section.",
    "All ten cards and full reviews remain readable without JavaScript.",
    "No browser JavaScript errors during these checks."
  ],
  "javascriptErrors": [],
  "limits": "Local browser emulation only. Not physical-device, Safari, Firefox, accessibility certification or real-money operator testing."
}


## Review order and card-details structural checks — 16 November 2026

```json
{
  "date": "2026-11-16",
  "reviewPlacement": "Immediately after #overview",
  "cardsWithFacts": 10,
  "factFields": 60,
  "reviews": 10,
  "logosUnchanged": true,
  "affiliateLinksUnchanged": true,
  "coreCssUnchanged": true,
  "duplicateIds": 0,
  "brokenInternalAnchors": 0,
  "ukAcceptance": "Unconfirmed; no affirmative acceptance labels added",
  "htmlSha256": "dc15ffe8b2eabc5d83a1a7ae09739eba432bd1bde10e8aec635a072cfff28cd8"
}
```

These are executed structural checks. Browser results, when executed, are recorded separately.


### Executed card-update browser checks

```json
{
  "engine": "Headless Chromium via Playwright",
  "checks": [
    "Ten cards, 60 facts, ten original logos and ten full reviews; reviews directly follow the overview.",
    "Search, sorting and the comparison modal show the new offer, spins, wagering, UK and payment fields.",
    "Read-review links and linked offer sources navigate correctly and reveal the collapsed source notes.",
    "No document-level horizontal overflow at 320, 360, 390, 590, 768, 1000 and 1440 pixels.",
    "The mobile menu closes after choosing a section.",
    "The expanded card information and all reviews remain in the initial HTML and readable without JavaScript."
  ],
  "javascriptErrors": [],
  "scope": "Local browser emulation only; not physical-device, cross-browser, real-money or operator-eligibility testing."
}
```
