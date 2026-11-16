"""Build the requested November update without altering the approved core design."""
from __future__ import annotations
import base64, copy, hashlib, json, re
from html import escape
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://nogamstop.github.io/best-casinos-not-on-gamstop-uk-non-gamstop-sites/'
EXPECTED_ORDER = ['donbet','goldenbet','betportal','mystake','wildies','betride','casinok','betfoxx','booming-slots','patrick-spins']
EXPECTED_BLOB = '44f75fcb3a4980abab086772643601a03c73fce1'
E = escape

def fragment(markup):
    return BeautifulSoup(markup, 'html.parser')

def replace_contents(tag, markup):
    assert tag is not None
    tag.clear()
    for child in list(fragment(markup).contents):
        tag.append(child)

def words(text):
    return len(re.findall(r"\b\w+(?:[’'-]\w+)*\b", text))

# The fourth selection is expected to be rejected, so click rather than assert checked.
qa_script = ROOT/'tools/check_november.py'
qa_script.write_text(qa_script.read_text().replace('inputs.nth(3).check(force=True)', 'inputs.nth(3).click(force=True)'))
raw = (ROOT / 'index.html').read_bytes()
blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
assert blob == EXPECTED_BLOB, 'Source HTML changed; inspect before rebuilding.'
data = json.loads((ROOT/'content/reviews-november-2026.json').read_text())
reviews = data['reviews']
assert [r['id'] for r in reviews] == EXPECTED_ORDER
links = json.loads((ROOT/'affiliate-links.json').read_text())
for entry in links['links']:
    if entry['url'] == 'https://btccasinos.net/go/okredgam':
        entry.update(casinoId='casinok', displayName='CasinoK', mappingStatus='CasinoK identity confirmed by the owner on 16 November 2026; redirect not independently verified.')
        entry.pop('proposedCasinoId', None)
        entry.pop('proposedDisplayName', None)
link_map = {entry['casinoId']:entry['url'] for entry in links['links']}
assert set(link_map) == set(EXPECTED_ORDER)
links['integrationStatus'] = 'Integrated into the ten Visit casino buttons in index.html.'
links['ownerConfirmedCasinoKOn'] = '2026-11-16'

logos = {}
for f in sorted((ROOT/'tools').glob('logos-*.json')):
    logos.update(json.loads(f.read_text()))
assert set(logos) == set(EXPECTED_ORDER), 'Expected ten supplied logos.'
# Correct transport transcription only; original SHA-256 remains authoritative.
logos['goldenbet']['data'] = logos['goldenbet']['data'].replace('O3KNHS/4f/+lWVIG', 'O3KNHS/4f//lWVIG')
logos['betride']['data'] = logos['betride']['data'].replace('J9z35t/cv95/g3d+', 'J9z35t/cv95/g/3d+')
logo_dir = ROOT/'assets/logos'
logo_dir.mkdir(parents=True, exist_ok=True)
for key, meta in logos.items():
    payload = base64.b64decode(meta['data'], validate=True)
    got = hashlib.sha256(payload).hexdigest()
    assert got == meta['sha256'], f'Logo checksum mismatch: {key}: {got}; bytes={len(payload)}'
    assert payload[:4] == b'RIFF' and payload[8:12] == b'WEBP'
    (logo_dir/meta['file']).write_bytes(payload)
    print(f'LOGO OK {key}: {len(payload)} bytes')

s = BeautifulSoup(raw.decode(), 'html.parser')
old_style = s.style.string
s.html['lang'] = 'en-GB'
for node in list(s.find_all(string=lambda t: t and t.strip() == 'Editorial preview')):
    node.parent.decompose()
replace_contents(s.select_one('.byline'), '<span class="avatar" aria-hidden="true">CN</span><span>By <strong>Casino Notes Editorial Team</strong></span><span class="separator" aria-hidden="true"></span><span>Last updated: <time datetime="2026-11-16">16 November 2026</time></span><span class="separator disclosure-separator" aria-hidden="true"></span><span class="disclosure-wrap"><a href="#editorial-disclosure" class="inline-button" data-dialog="about-dialog">About this comparison</a></span>')
for key, value, attr in [('author',data['author'],'name'), ('article:modified_time','2026-11-16','property'), ('og:url',URL,'property')]:
    node = s.find('meta',attrs={attr:key})
    if node is None:
        node=s.new_tag('meta',attrs={attr:key}); s.head.append(node)
    node['content']=value
canonical=s.find('link',rel='canonical')
if canonical is None:
    canonical=s.new_tag('link',rel='canonical'); s.head.append(canonical)
canonical['href']=URL
for comment in list(s.find_all(string=lambda t: t and 'Add a real canonical URL' in t)):
    comment.extract()
structured=s.new_tag('script',type='application/ld+json')
structured.string=json.dumps({'@context':'https://schema.org','@type':'Article','headline':s.title.get_text(),'url':URL,'inLanguage':'en-GB','dateModified':'2026-11-16','author':{'@type':'Organization','name':data['author']}},ensure_ascii=False)
s.head.append(structured)
s.select_one('#list-title').string=data['heading']
s.select_one('.list-head p').string='Ten detailed reviews: features, terms and risks, with sources for the key findings.'
s.select_one('#site-count').string='10 sites'
replace_contents(s.select_one('.filters'), '<button type="button" class="filter" data-filter="all" aria-pressed="true">All sites <span>10</span></button><button type="button" class="filter" data-filter="partial" aria-pressed="false">Source reviews <span>6</span></button><button type="button" class="filter" data-filter="warning" aria-pressed="false">Read cautions <span>4</span></button>')
s.select_one('.filters')['aria-label']='Filter casinos by review status'
replace_contents(s.select_one('.list-caption > span'), '<strong>Published-information reviews</strong> · Not a safety ranking')
replace_contents(s.select_one('#casino-sort'), '<option value="listed">Listed order</option><option value="asc">Name: A to Z</option><option value="desc">Name: Z to A</option>')
notice=fragment('<p class="affiliate-notice"><strong>Advertisement · Affiliate links.</strong> We may earn commission through the Visit casino links. Listing a brand is not a safety endorsement or confirmation of UK eligibility. Read each review, including any warnings. <a href="#editorial-disclosure">How this page is funded</a>.</p>').p
s.select_one('.list-head').insert_after(notice)

container=s.select_one('#casino-cards')
template=copy.deepcopy(s.select_one('.casino-card'))
container.clear()
for number, r in enumerate(reviews,1):
    rid=r['id']; name=r['name']; meta=logos[rid]
    card=copy.deepcopy(template)
    card.attrs.update({'id':f'card-{rid}','data-brand':rid,'data-name':name,'data-status':r['status'],'aria-labelledby':f'{rid}-title'})
    replace_contents(card.select_one('.card-top-title'),f'<span class="list-number">{number:02}</span> Casino review')
    card.select_one('.status').string=r['label']
    card.select_one('.status')['class']=['status',r['status']]
    logo=card.select_one('.casino-logo'); logo['class']=['casino-logo','supplied-logo']; logo.attrs.pop('aria-hidden',None)
    replace_contents(logo,f'<img src="assets/logos/{meta["file"]}" alt="{E(name)} logo" width="{meta["width"]}" height="{meta["height"]}" loading="lazy" decoding="async"/>')
    title=card.select_one('.casino-identity h3'); title['id']=f'{rid}-title'; title.string=name
    card.select_one('.casino-identity small').string='Casino profile · 18+'
    card.select_one('.offer-label').string=r['focus']
    replace_contents(card.select_one('.offer-title'),E(r['offer'])+f'<span>{E(r["offerDetail"])}</span>')
    replace_contents(card.select_one('.check-items'),''.join(f'<li><span class="feature-tick" aria-hidden="true">•</span>{E(item)}</li>' for item in r['checks']))
    replace_contents(card.select_one('.score-placeholder'),'<strong>Terms-first review</strong>No first-hand gambling tests')
    cta=card.select_one('a.cta'); cta['href']=link_map[rid]; cta['target']='_blank'; cta['rel']=['nofollow','sponsored','noopener']; cta['aria-label']=f'Visit {name} — affiliate link, opens in a new tab'; cta['data-affiliate']=rid
    replace_contents(cta,'Visit casino <span aria-hidden="true">↗</span>')
    review_link=card.select_one('.small-link'); review_link['href']=f'#review-{rid}'; review_link['class']=['review-link']; review_link.string='Read review'
    card.select_one('.card-foot-note').string='Affiliate link · Terms and eligibility apply'
    checkbox=card.select_one('.compare-checkbox'); checkbox['value']=rid; checkbox['aria-label']=f'Add {name} to comparison'
    details=card.select_one('.card-notes'); details['id']=f'{rid}-note'
    replace_contents(details.summary,'Quick review notes <span aria-hidden="true">⌄</span>')
    replace_contents(details.select_one('.note-content'),f'<p>{E(r["summary"])}</p><p><strong>Evidence:</strong> {E(r["evidence"])}. <strong>Limit:</strong> {E(r["limitation"])}.</p><p><a class="review-link" href="#review-{rid}">Read the full {E(name)} review →</a></p>')
    container.append(card)

s.select_one('.fineprint').string='The order follows the publisher’s selected list, not a best-to-worst safety ranking. These reviews assess published information, not first-hand gambling tests. No new-launch date or UK eligibility is assumed. Supplied logos identify the brands and do not establish endorsement. Where concerns are documented, they are included in the review.'
section=fragment('<section class="detailed-reviews" id="casino-reviews" aria-labelledby="reviews-title"><div class="reviews-intro"><span class="section-kicker">Read beyond the headline</span><h2 id="reviews-title">Detailed casino reviews</h2><p>Published terms, relevant features and important limitations. The author is Casino Notes Editorial Team; these are not first-hand deposit or withdrawal tests.</p></div></section>').section
counts={}
for r in reviews:
    rid=r['id']; name=r['name']
    text=' '.join(part['text'] for part in r['sections'])
    count=words(text); counts[name]=count
    assert 440 <= count <= 580, f'Review length outside agreed range: {name}: {count}'
    article=fragment(f'<article class="article-section casino-review" id="review-{rid}" aria-labelledby="review-title-{rid}"><header class="article-heading"><p class="section-number">{E(r["focus"])}</p><h3 id="review-title-{rid}">{E(name)} review</h3><p>{E(r["summary"])}</p></header><div class="prose review-copy"></div></article>').article
    prose=article.select_one('.review-copy')
    for part in r['sections']:
        refs=' '.join(f'<a class="ref" href="#review-{rid}-source-{i}" aria-label="{E(name)} source {i}">[{i}]</a>' for i in part.get('sources',[]))
        markup=f'<h4>{E(part["heading"])}</h4><p>{E(part["text"])} {refs}</p>'
        for node in list(fragment(markup).contents): prose.append(node)
    source_items=''.join(f'<li id="review-{rid}-source-{i}"><a href="{E(source["url"],quote=True)}" target="_blank" rel="noopener">{E(source["label"])}</a></li>' for i,source in enumerate(r['sources'],1))
    sources=fragment(f'<details class="review-sources"><summary>Sources and research notes</summary><p>Sources accessed for this update on 16 November 2026. Publication dates and the age of individual observations may differ. Operator claims and secondary assessments are not independently verified account outcomes.</p><ol>{source_items}</ol></details>').details
    article.append(sources)
    article.append(fragment('<p class="back-to-list"><a href="#casino-list">↑ Back to the casino comparison</a></p>').p)
    section.append(article)
    print(f'REVIEW WORDS {name}: {count}')
s.select_one('.explore').insert_before(section)

nav=fragment('<a href="#casino-reviews">Full reviews</a>').a
s.select_one('.jump-inner a').insert_after(nav)
toc=fragment('<a href="#casino-reviews"><span>02</span>Detailed casino reviews</a>').a
s.select_one('.toc a').insert_after(toc)
for n,link in enumerate(s.select('.toc a'),1):
    if link.span: link.span.string=f'{n:02}'

replace_contents(s.select_one('.dark-band p'),'This edition includes affiliate links, clearly identified beside the comparisons. The reviews assess published information, not first-hand gambling tests. No invented ratings, fabricated authors or unsupported instant-payout claims are used. Unverified does not mean approved.')
s.select_one('#disclosure-heading').string='Advertisement and editorial disclosure'
s.select_one('#editorial-disclosure .source-intro').string='The Visit casino buttons are affiliate links supplied by the publisher. We may earn a commission when a reader follows a link and uses the destination service. The ten brands were selected by the publisher; their order is not a safety ranking. Reviews use published operator information, regulatory notices and identified independent sources. No gambling accounts, deposits, withdrawals or support journeys were tested. A listed site is not necessarily authorised for your location. Commercial links do not override the warnings or research limitations shown.'
s.select_one('.about-dialog .dialog-header p').string='Sources, limitations and commercial links.'
replace_contents(s.select_one('.about-dialog .dialog-body'),'<p>This page reviews ten publisher-selected brands using published information. Their order is not a safety ranking, and inclusion is not a blanket recommendation.</p><h3>How is this page funded?</h3><p>Visit casino buttons contain affiliate links. We may earn commission through those links. They are labelled and marked as sponsored in the page code.</p><h3>What has actually been checked?</h3><p>The reviews distinguish operator statements, independent reporting and regulatory notices. No accounts were opened and no deposits, withdrawals or support services were tested. Exact destinations, UK eligibility and licence coverage have not been independently certified.</p><p><a class="cta" data-close-and-navigate="" href="#casino-reviews">Read the detailed reviews →</a></p>')
s.select_one('.footer-note').string='Casino Notes is an informational editorial project for adults, not a casino or a regulator. It is not affiliated with GAMSTOP, Casino.org or Gambling.com. This page contains affiliate links, and the publisher may receive commission. Brand inclusion and supplied logos do not establish approval, UK authorisation or an independent safety endorsement. Read the individual warnings and conditions.'
s.select_one('.privacy p').string='This page does not add analytics, advertising cookies, accounts, contact forms or browser storage. Search and comparison selections are kept in memory and reset when the page reloads. Styles and scripts are included in the HTML; supplied logo images are hosted with the site. The hosting provider may process connection logs. External affiliate redirects and casino websites may use their own tracking and privacy practices. Casino Notes Editorial Team is the byline specified by the publisher; no individual qualifications, personal testing history or registered-company status is implied.'
s.select_one('.footer-bottom > span').string='© 2026 Casino Notes · 18+ · UK edition'
for node in list(s.find_all(string=True)):
    if node.parent and node.parent.name not in ('script','style') and 'This preview' in node:
        node.replace_with(str(node).replace('This preview','This guide'))

profiles=[{k:r[k] for k in ['id','name','label','evidence','limitation','offer','offerDetail']} for r in reviews]
s.select_one('#casino-data').string=json.dumps(profiles,ensure_ascii=False)
ui=next(t for t in s.find_all('script') if t.string and "sort.addEventListener" in t.string)
code=ui.string
needle="      const order = a.dataset.name.localeCompare(b.dataset.name, 'en-GB');"
assert code.count(needle)==1
code=code.replace(needle,"      if (sort.value === 'listed') return profiles.findIndex(p => p.id === a.dataset.brand) - profiles.findIndex(p => p.id === b.dataset.brand);\n"+needle)
code=code.replace("['Welcome offer', () => 'Not verified']","['Offer note', profile => profile.offerDetail]")
ui.string=code
extra_css='''\n/* November review expansion: preserve the approved core design. */
.affiliate-notice{font-size:11px;line-height:1.8;color:#5b6578;margin:0 0 17px;padding:12px 14px;background:#fff7e4;border:1px solid #f0dfb6;border-radius:7px}.affiliate-notice a{text-decoration:underline;text-underline-offset:2px}.casino-logo.supplied-logo{height:112px;background:#111a26}.casino-logo.supplied-logo:after{display:none}.supplied-logo img{display:block;width:100%;height:100%;object-fit:contain}.review-link{display:block;font-size:11px;font-weight:700;color:var(--teal);text-decoration:underline;text-underline-offset:3px;margin-top:9px}.status.warning{background:#fff0e8;border-color:#f0c9ae;color:#8c3b1b}.feature-tick{color:var(--teal);font-weight:800}.offer-label{line-height:1.6}.reviews-intro{margin:35px 0 20px}.reviews-intro h2{font-size:27px}.reviews-intro p{font-size:13px;line-height:1.85;color:var(--muted);margin-top:10px}.casino-review .article-heading h3{font-size:26px}.review-copy h4{font-size:17px;line-height:1.5;margin:24px 0 10px;color:var(--ink);letter-spacing:-.2px}.review-copy h4:first-child{margin-top:0}.review-sources{font-size:11px;color:#59677b;border-top:1px solid var(--line);padding-top:15px;margin-top:23px;overflow-wrap:anywhere}.review-sources summary{font-weight:700;cursor:pointer;color:var(--teal)}.review-sources p{margin-top:12px;line-height:1.8}.review-sources li{margin-top:8px}.review-sources a{text-decoration:underline;text-underline-offset:2px}.back-to-list{font-size:11px;font-weight:700;color:var(--teal);margin-top:18px}.card-action .cta{width:100%}.card-action .review-link{align-self:center}.card-top-title{flex-shrink:0}.status{white-space:normal;text-align:right}.byline{row-gap:8px}
@media(max-width:1000px){.card-action .review-link{grid-column:2;grid-row:2;text-align:center;margin-top:0}.card-action{row-gap:8px}}
@media(min-width:591px) and (max-width:780px){.card-action .review-link{margin-top:9px}}
@media(max-width:590px){.casino-logo.supplied-logo{height:100px}.affiliate-notice{font-size:10px}.casino-review .article-heading h3{font-size:23px}.review-copy h4{font-size:16px}.reviews-intro h2{font-size:23px}.status{font-size:8px}.card-top-title{font-size:9px}.offer-title{font-size:19px}.byline{font-size:10px}}
'''
s.style.string=old_style+extra_css
out=str(s)
(ROOT/'index.html').write_text(out,encoding='utf-8')
(ROOT/'affiliate-links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2)+'\n')

ids=[tag['id'] for tag in s.find_all(id=True)]
assert len(ids)==len(set(ids)), 'Duplicate IDs'
missing=[a['href'] for a in s.select('a[href^="#"]') if len(a['href'])>1 and a['href'][1:] not in ids]
assert not missing, f'Broken internal links: {missing}'
assert len(s.select('h1'))==1
assert len(s.select('.casino-card'))==10 and len(s.select('.casino-review'))==10
assert s.select_one('#list-title').get_text()==data['heading']
assert 'Editorial preview' not in s.get_text()
assert len(s.select('a[data-affiliate]'))==10
for a in s.select('a[data-affiliate]'):
    assert a['href']==link_map[a['data-affiliate']]
    assert {'sponsored','nofollow','noopener'} <= set(a['rel'])
    assert a['target']=='_blank'
assert len(s.select('.supplied-logo img'))==10
assert not re.search('[\u0400-\u04ff]',out), 'Unexpected Cyrillic text'
report={'date':data['modified'],'author':data['author'],'reviewBodyWordCounts':counts,'totalReviewBodyWords':sum(counts.values()),'cards':10,'logos':10,'affiliateLinks':10,'duplicateIds':0,'brokenInternalLinks':0,'htmlSha256':hashlib.sha256(out.encode()).hexdigest(),'originalCoreCssPreserved':True,'browserChecks':'Not yet run by this build script.'}
(ROOT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'ui-check.js').write_text(code)

readme='''# Best Casinos Not On GamStop UK — New Sites Not On GamStop

A single-page British English website using the approved navy, mint and yellow comparison design.

**Website:** '''+URL+'''

## November 2026 update

- Ten detailed, sourced reviews, approximately 500 words each.
- Byline: **Casino Notes Editorial Team**.
- Visible last-updated date: **16 November 2026**.
- Ten owner-supplied logos, stored locally as optimised WebP images without cropping or redrawing.
- External **Visit casino** affiliate buttons and internal **Read review** links.
- Search, evidence-status filters, listed/alphabetical sorting and comparison of up to three brands.
- The content remains readable without JavaScript.

The headline is the publisher's requested topic, not a certification that every listed operator is safe or authorised for Great Britain. Regulatory notices and attributed concerns appear in the relevant reviews. No account, deposit, withdrawal or support tests were performed. The reviews distinguish operator statements, secondary reporting and editorial assessment. There are no fabricated scores or guarantees.

## Editing

`index.html` contains the rendered page, styles and interactive code. `content/reviews-november-2026.json` records the review copy and sources; changes to this data file alone do not update the rendered HTML. `affiliate-links.json` records the publisher-supplied destinations and their exact tracking paths. `assets/logos/` contains the supplied logo assets.

Keep the rendered HTML, review data and affiliate mapping consistent when editing. Use British English throughout. Do not add keys, passwords or personal account data to this public repository.

## Local preview

Download or clone the repository and run:

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. No build system, database, remote font or external JavaScript library is required by the published page.

## Publishing and commercial disclosure

GitHub Pages is configured to publish the repository's `main` branch. A successful repository commit is not itself proof that the associated deployment has completed. Check the Pages deployment result after changes.

Visit casino buttons are publisher-supplied affiliate links and carry `rel="nofollow sponsored noopener"`. Their exact redirects and jurisdictional eligibility have not been independently certified. The CasinoK mapping was explicitly confirmed by the owner. External destinations have their own terms and privacy practices.

Before operating a commercial affiliate service, review the host's permitted-use conditions and the applicable licensing and advertising requirements. GitHub Pages has restrictions on use as free hosting for online business; the source repository can remain public if the website moves to suitable hosting.

## Checks

See `QA.md` for the checks actually performed and their limits. `CHANGELOG.md` records the project updates. No regulator endorsement, personal author credentials or independent casino testing is implied by the editorial team name.
'''
(ROOT/'README.md').write_text(readme)
changelog=ROOT/'CHANGELOG.md'
changelog.write_text('# Changelog\n\n## November reviews and supplied branding — 16 November 2026\n\n- Added ten approximately 500-word published-information reviews with source notes and relevant warnings.\n- Added the requested list heading, editorial team byline and modification date.\n- Removed the Editorial preview label without concealing evidence limitations.\n- Integrated the ten exact publisher-supplied affiliate URLs and CasinoK confirmation.\n- Added ten optimised supplied logos and kept the original core design.\n- Updated commercial disclosures, comparison data, filters and navigation.\n\n'+changelog.read_text())
qa=ROOT/'QA.md'
qa.write_text('# November update — structural QA\n\n'+json.dumps(report,indent=2)+'\n\nWord counts cover review body paragraphs, excluding headings, cards and source lists. Checks above were executed by the build script. Browser checks, when run, are recorded separately below. The earlier report below describes the previous design, not a new run against this update.\n\n'+qa.read_text())
print(json.dumps(report,indent=2))
