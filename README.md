# Best Casinos Not On GamStop UK — New Sites Not On GamStop

Best Online Casinos Not On GamStop UK - Non GamStop Sites

Public repository for the approved **Casino Notes, v2** single-page website. The website and project documentation use **British English (en-GB)**.

## Project status

The approved design is stored as `index.html` in the root of the `main` branch. Its text, layout, CSS and JavaScript remain unchanged from the approved version.

The repository contains the website source code. At the last settings check, GitHub Pages had not been enabled. Adding `.nojekyll` prepares the static files for publishing but does not activate hosting by itself. No custom domain has been configured and no request for Google indexing has been submitted as part of this work.

The content remains an editorial and design preview, not a completed or independently verified casino ranking.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The complete page, including British English copy, CSS, JavaScript, SVG illustrations and interactive features. |
| `README.md` | Instructions for opening, editing and publishing the project. |
| `CHANGELOG.md` | The approved v2 design changes and subsequent repository updates. |
| `QA.md` | Recorded design checks, upload verification and subsequent documentation checks. |
| `.gitignore` | Exclusions for local settings, temporary files and common secret-file patterns. |
| `.nojekyll` | An empty marker file that disables Jekyll processing when publishing the static site through GitHub Pages. |

The PNG previews from the downloadable package are not included in the repository. They are not required by the website: its illustration and icons are embedded in the HTML.

## Open the website locally

Select **Code → Download ZIP**, extract the archive and open `index.html` in a browser. No installation, compilation, database, API or external library is required.

For a local HTTP preview, with Python already installed, run this command from the project folder:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. Press **Ctrl+C** in the terminal to stop the server.

## Publish a GitHub Pages preview

The files are ready for a branch-based static deployment. A repository administrator or maintainer must enable the publishing source in GitHub:

1. Open **Settings → Pages** in this repository.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Select **main** as the branch and **/ (root)** as the folder.
4. Select **Save**.
5. Check the deployment status in **Actions** and use **Visit site** in the Pages settings after a successful deployment.

With the current account and repository names, and no custom domain, the expected address after deployment is:

```text
https://nogamstop.github.io/best-casinos-not-on-gamstop-uk-non-gamstop-sites/
```

This is the intended website address, not a claim that the site is already live. There is no need to add `index.html` to the end of the address.

GitHub Pages must be used in accordance with GitHub's terms. It is not permitted as free hosting for an online business or a website primarily intended to facilitate commercial transactions. Review the usage restrictions before publishing; choose suitable hosting for a commercial affiliate launch.

Official guidance:

- [Configure a GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
- [GitHub Pages usage limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## Features

The page includes name search, research-status filters, alphabetical sorting, two- or three-site comparisons, expandable review notes, an editorial disclosure dialogue box, mobile navigation, FAQs, internal source links and a reading-progress indicator.

Search, filtering and comparisons use JavaScript. The main text, casino cards and expandable notes remain available without JavaScript. Comparison selections are stored only in memory and are cleared when the page is reloaded.

The prominent **Read review** buttons open internal notes. They are not affiliate destinations and do not direct visitors to registration or deposit pages. The coloured operator names are typographic labels, not official logos.

## Editing

All website code is in `index.html`. Colours are defined as CSS custom properties in `:root`, the page title appears in the single `<h1>`, and metadata is stored in `<head>`.

To edit a casino card, find its `data-brand` attribute, such as `data-brand="donbet"`. Comparison data is stored in `<script id="casino-data" type="application/json">`. Update both the visible card and its corresponding JSON entry. When adding or removing entries, also update the initial counts displayed on the filters.

Use British English for public-facing copy, documentation, comments and new commit messages. Preserve exact API names, programming keywords, brand names and interface labels where required. For example, CSS uses `color` and `center`; these must not be translated.

Never commit passwords, API keys, access tokens or personal data. `.gitignore` does not remove secrets that have already been published or committed to the repository's history.

## Before a public editorial or affiliate launch

1. Choose the final project name, publisher details and contact information. **Casino Notes** is a working name.
2. Verify current operator details, territorial restrictions, offers and the evidence supporting each assessment. The order of the cards is not a quality ranking.
3. Review applicable licensing and advertising requirements before adding commercial or affiliate links.
4. Choose suitable hosting and the final public website address. Then add accurate `canonical` and `og:url` values and a social sharing image. Do not use the GitHub repository address as the live website address.
5. Update the privacy and commercial disclosure information when adding analytics, cookies, forms or affiliate tracking.

## Design and content

The original interface uses a navy header, mint accents, yellow buttons, casino cards, desktop section navigation and a responsive mobile layout. Casino.org and Gambling.com informed the general type of layout; their logos, CSS and articles were not copied.

The initial notes for Donbet, Freshbet, Goldenbet and MyStake are retained. No invented ratings, bonuses, withdrawal tests or launch dates have been added. Unverified fields remain labelled.

## Approved HTML integrity

- File size: **107,154 bytes**.
- Git blob SHA: `44f75fcb3a4980abab086772643601a03c73fce1`.
- SHA-256: `98b93d66c4eaee414218ea4dc1ad2aff28627c53500eca31eb7d3d994657beca`.

These values identify the approved HTML initially uploaded to the repository. The documentation update does not change that file. Future website edits will normally change its checksums.
