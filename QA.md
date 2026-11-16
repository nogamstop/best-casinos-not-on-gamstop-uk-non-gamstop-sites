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
