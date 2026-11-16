"""Reorder existing review sections and add attributed comparison-card facts.

This is an editorial data update, not live gambling-account verification.
"""
from pathlib import Path
from html import escape
import json, re, hashlib
from bs4 import BeautifulSoup

ROOT = Path.cwd()
DATE = '2026-11-16'
DATA = [
 dict(id='donbet', kind='Reported welcome offer', offer='150% up to €750', detail='+ 50 free spins · directory-listed', spins='50 (reported)', deposit='€20 (reported)', wagering='30× deposit + bonus + spin winnings (reported)', payments='Bitcoin and other methods listed', withdrawals='€7,500/week; €15,000/month (reported)', terms='Casino Guru lists the match and spins; the indexed Bitcoin.com review reports the deposit and wagering conditions, a €5 maximum bonus bet and a 30-day deadline. These are secondary reports, not a confirmed offer for a UK account.', sources=[['Casino Guru — reported offer, payments and limits','https://casino.guru/donbet-casino-review'],['Bitcoin.com — indexed bonus-terms report; direct page is region-dependent','https://www.bitcoin.com/gambling/reviews/donbet/']]),
 dict(id='goldenbet', kind='Operator-published weekly offer', offer='Up to 200 free spins', detail='100 on Thursday + 100 on Friday', spins='100 per qualifying day', deposit='€50 / £50 on each day', wagering='Wager-free winnings on this offer', payments='Check the current cashier', withdrawals='€1,000 / £1,000 spin-winnings cap', terms='This is a recurring promotion, not a verified welcome package. The indexed operator page names Hot Chilli Bells, code GOLDEN and activation within one hour of depositing. A separate qualifying deposit is needed on each of the two days. The specific offer has its own cashout limit; do not apply it to other bonuses.', sources=[['Goldenbet — indexed weekly free-spin promotion and specific conditions','https://goldenbet.com/static/promos?pid=11739']]),
 dict(id='betportal', kind='Reported first-deposit offer', offer='150% up to €500', detail='Free-spin allocation needs confirmation', spins='Reports differ: 20 to 200', deposit='€20 (reported)', wagering='35× bonus (reported)', payments='Bitcoin listed; GBP account currency reported', withdrawals='Current operator limits not confirmed', terms='Mr Gamble lists 20 first-deposit spins; CashToCode reports a deposit-dependent allocation of 20–200. The operator promotion page did not expose readable offer conditions during research. The figures are attributed reports, not a reconciled or UK-verified package.', sources=[['Mr Gamble — reported first-deposit offer and conditions','https://mr-gamble.com/en/online-casino/betportal-casino/'],['CashToCode — reported deposit-dependent spin allocation','https://cashtocode.com/ir/casinos/betportal-casino'],['Casino Guru — payment and currency listing','https://casino.guru/betportal-casino-review'],['Betportal — operator promotion page; offer text not retrievable','https://betportal.com/en/promotions']]),
 dict(id='mystake', kind='Operator-published welcome package', offer='Up to €1,500 / $1,500', detail='150% + 100% + 50% across 3 deposits', spins='Not specified in this package', deposit='€20 / $20 per qualifying deposit', wagering='30× deposit + bonus', payments='Crypto payments reported', withdrawals='Current account limits not confirmed', terms='The indexed operator terms split the package into 150% up to €/$750, 100% up to €/$500 and 50% up to €/$250. Slots only; maximum bonus bet €/$5; 30-day wagering deadline. Each stage is optional and must be activated before playing. No free-spin entitlement is specified in this particular package.', sources=[['MyStake — indexed welcome-package terms','https://www.mystake.com/promotions?id=3221'],['Casino Guru — reported cryptocurrency payments','https://casino.guru/mystake-casino-review']]),
 dict(id='wildies', kind='Reported welcome offer', offer='150% up to €1,000', detail='+ 100 free spins · directory-listed', spins='100 (reported)', deposit='Not confirmed from operator terms', wagering='Not confirmed from operator terms', payments='BTC, BCH, DOGE and bank transfer listed', withdrawals='€500/day; €2,000/week; €8,000/month (reported)', terms='Casino Guru lists this offer and payment limits. The current operator bonus rules were not retrievable; no wagering figure or minimum deposit has been inferred from similarly named websites. Reported limits are not measured payout times.', sources=[['Casino Guru — reported offer, methods and withdrawal limits','https://casino.guru/wildies-casino-review']]),
 dict(id='betride', kind='Operator-published casino offer', offer='200 free spins', detail='Code BR200 · selected slot only', spins='200 at €0.20 each', deposit='€100 or equivalent', wagering='Wager-free winnings on this offer', payments='Crypto promotion published; cashier untested', withdrawals='€5,000 spin-winnings cap', terms='The indexed casino offer names Fruit Million by BGaming. Code BR200 is single-use, with a one-hour activation window after the deposit and a one-hour use window stated in the promotion. This is separate from the crypto welcome promotion discussed in the review, which has different deposit and wagering rules.', sources=[['Betride — indexed 200-free-spin promotion','https://betride.com/en/static/promos?pid=7588'],['Betride — separate indexed crypto-promotion conditions','https://betride.com/']]),
 dict(id='casinok', kind='Reported deposit offer', offer='100% up to $2,000', detail='Directory-listed · amount retained in USD', spins='Not specified in the cited offer', deposit='Not confirmed from operator terms', wagering='Not confirmed from operator terms', payments='Visa, Mastercard, BTC and USDT listed', withdrawals='100,000 USDC/week (directory-listed)', terms='Casino Guru lists three 100% deposit offers with a $2,000 ceiling each. We have not combined them into a guaranteed package or converted the amount to pounds. The directory also reports a 250,000 USDC monthly limit; actual methods, limits and bonus eligibility require current operator confirmation.', sources=[['Casino Guru — reported deposit offers, payment methods and limits','https://casino.guru/casinok-casino-review']]),
 dict(id='betfoxx', kind='Reported offer — read the warning', offer='200% up to €20,000', detail='+ 100 free spins · not operator-confirmed', spins='100 (reported)', deposit='Not confirmed from operator terms', wagering='Not confirmed from operator terms', payments='Bitcoin listed; cashier untested', withdrawals='€500/week (reported)', terms='Casino Guru lists the promotional figure and withdrawal ceiling. They are not a recommendation or a verified UK offer. A Kahnawà:ke Gaming Commission notice dated 12 September 2024 says BetFoxx was not licensed by that commission and was claiming its authority improperly. That dated notice does not establish every possible current licensing status.', sources=[['Casino Guru — reported offer and withdrawal limit','https://casino.guru/betfoxx-casino-review'],['Kahnawà:ke Gaming Commission — advisory of 12 September 2024','https://gamingcommission.ca/betfoxx-is-not-licensed-by-the-kahnawake-gaming-commission/']]),
 dict(id='booming-slots', kind='Reported deposit offer', offer='200% up to €2,000', detail='+ 100 free spins · one listed offer', spins='100 with the cited deposit offer', deposit='Not confirmed from operator terms', wagering='Not confirmed from operator terms', payments='Current methods not confirmed', withdrawals='Low limits reported; amount not confirmed', terms='Casino Guru lists this alongside separate 200% offers capped at €500 and €1,000, with different spin allocations. We have not assumed which offer applies to a first deposit or combined separate alternatives. The directory also flags licensing and withdrawal-limit concerns; these remain visible in the detailed review.', sources=[['Casino Guru — listed deposit offers and reported concerns','https://casino.guru/boomingslots-casino-review']]),
 dict(id='patrick-spins', kind='Reported deposit offer', offer='150% up to €1,000', detail='Directory-listed · not a verified UK offer', spins='Not specified in the cited offer', deposit='Not confirmed from operator terms', wagering='Not confirmed from operator terms', payments='BTC, USDT and Polygon listed', withdrawals='€2,000/day; €5,000/month (reported)', terms='Casino Guru lists 150%, 125% and 175% offers capped at €1,000 each. The cited listing does not specify a free-spin entitlement for the selected offer. The reported withdrawal limits are not payout-time promises, and the current operator terms and UK eligibility remain unconfirmed.', sources=[['Casino Guru — reported offers, crypto methods and withdrawal limits','https://casino.guru/patrick-spins-casino-review']])
]
for d in DATA:
    d['ukPlayers'] = 'Not confirmed by current operator terms'
    d['retrievedOn'] = DATE
    d['sourceStatus'] = 'Indexed operator text' if d['kind'].startswith('Operator') else 'Secondary reports — not operator-confirmed'

html_path = ROOT / 'index.html'
original = html_path.read_text(encoding='utf-8')
soup = BeautifulSoup(original, 'html.parser')
assert len(soup.select('.casino-card')) == 10
assert len(soup.select('.casino-review')) == 10
original_core_css = str(soup.find('style'))
original_links = [(a.get('data-affiliate'), a.get('href')) for a in soup.select('a[data-affiliate]')]
original_logos = [str(a) for a in soup.select('.casino-card img')]
original_reviews = {a['id']:a.select_one('.review-copy').get_text(' ',strip=True) for a in soup.select('.casino-review')}

def fragment(text):
    return BeautifulSoup(text, 'html.parser')

def replace_children(node, text):
    node.clear()
    for child in list(fragment(text).contents):
        node.append(child)

# Keep the top comparison list, then explain the topic, then provide full reviews.
review_section = soup.select_one('#casino-reviews').extract()
soup.select_one('#overview').insert_after(review_section)
soup.select_one('#overview-title').string = 'What are non-GamStop casinos?'
toc = soup.select_one('.toc')
review_nav = toc.select_one('a[href="#casino-reviews"]').extract()
toc.select_one('a[href="#overview"]').insert_after(review_nav)
for number, link in enumerate(toc.find_all('a', recursive=False), 1):
    if link.find('span'):
        link.find('span').string = f'{number:02d}'

# A single explanation applies to the full comparison, rather than ten copied disclaimers.
legend = soup.select_one('#offer-evidence-note')
if legend:
    legend.decompose()
legend = fragment('<p class="offer-evidence-note" id="offer-evidence-note"><strong>How to read the offers:</strong> operator-published terms and directory-listed figures are labelled separately. Source material was retrieved on 16 November 2026; this is not a live eligibility check. Currencies are shown as published, not converted to GBP. UK acceptance is not confirmed, and accepting a registration would not establish UKGC authorisation. <a href="#s1">Licensing explained</a>.</p>').p
soup.select_one('.list-tools').insert_before(legend)

profiles = json.loads(soup.select_one('#casino-data').string)
content_path = ROOT / 'content/reviews-november-2026.json'
content = json.loads(content_path.read_text(encoding='utf-8'))
for d in DATA:
    cid = d['id']
    card = soup.select_one('#card-' + cid)
    card.select_one('.offer-label').string = d['kind']
    replace_children(card.select_one('.offer-title'), escape(d['offer']) + '<span>' + escape(d['detail']) + '</span>')
    # Keep existing feature notes, removing only stale statements that no figures are displayed.
    for li in card.select('.check-items li'):
        if any(x in li.get_text().lower() for x in ['current offer needs', 'current bonus not independently', '45×']):
            replace_children(li, '<span class="feature-tick" aria-hidden="true">•</span>Offer terms and source details below')
    old_grid = card.select_one('.card-facts')
    if old_grid:
        old_grid.decompose()
    fields = [('Free spins','spins'),('Qualifying deposit','deposit'),('Wagering','wagering'),('UK players','ukPlayers'),('Payment methods','payments'),('Withdrawal / cashout','withdrawals')]
    facts = '<dl class="card-facts" aria-label="'+escape(card['data-name'])+' offer and account information">'
    for label,key in fields:
        facts += '<div><dt>'+label+'</dt><dd>'+escape(d[key])+'</dd></div>'
    facts += '</dl>'
    card.select_one('.card-main').insert_after(fragment(facts).dl)
    details = card.select_one('.card-notes')
    replace_children(details.select_one('summary'), 'Offer details &amp; sources <span aria-hidden="true">⌄</span>')
    for old in details.select('.card-offer-evidence'):
        old.decompose()
    sources = ''.join('<li><a href="'+escape(url,quote=True)+'" target="_blank" rel="noopener">'+escape(label)+'</a></li>' for label,url in d['sources'])
    evidence = '<div class="card-offer-evidence" id="offer-source-'+cid+'"><p><strong>'+escape(d['sourceStatus'])+'.</strong> '+escape(d['terms'])+'</p><ul>'+sources+'</ul><p class="evidence-date">Source retrieval: <time datetime="'+DATE+'">16 November 2026</time>. Availability and exact terms may change. No UK registration, deposit or withdrawal was tested.</p></div>'
    details.select_one('.note-content').append(fragment(evidence).div)
    # Keep comparison data in sync with the visible cards.
    for p in profiles:
        if p['id'] == cid:
            p.update(offer=d['offer'], offerDetail=d['detail'], freeSpins=d['spins'], minDeposit=d['deposit'], wagering=d['wagering'], ukPlayers=d['ukPlayers'], payments=d['payments'], withdrawals=d['withdrawals'], offerEvidence=d['sourceStatus'])
    for review in content['reviews']:
        if review['id'] == cid:
            review['offer'] = d['offer']
            review['offerDetail'] = d['detail']
            review['cardDetails'] = d
    # Link each long review to the newly added facts without rewriting its ~500-word body.
    full_review = soup.select_one('#review-' + cid)
    old_note = full_review.select_one('.review-offer-note')
    if old_note:
        old_note.decompose()
    linknote = fragment('<p class="review-offer-note"><strong>Offer information:</strong> '+escape(d['offer'])+' — '+escape(d['sourceStatus'].lower())+'. <a href="#offer-source-'+cid+'">See the card’s conditions, limits and sources</a>. UK eligibility remains unconfirmed.</p>').p
    full_review.select_one('.article-heading').insert_after(linknote)

soup.select_one('#casino-data').string = json.dumps(profiles, ensure_ascii=False).replace('</','<\\/')
# The comparison modal must show the same concrete data, not the old generic placeholders.
script = next(s for s in soup.find_all('script') if not s.get('type') and 'const fields = [' in s.get_text())
js = script.get_text()
replacement = """const fields = [
      ['Offer', profile => profile.offer],
      ['Offer details', profile => profile.offerDetail],
      ['Free spins', profile => profile.freeSpins],
      ['Qualifying deposit', profile => profile.minDeposit],
      ['Wagering', profile => profile.wagering],
      ['UK players', profile => profile.ukPlayers],
      ['Payment methods', profile => profile.payments],
      ['Withdrawal / cashout', profile => profile.withdrawals],
      ['Offer evidence', profile => profile.offerEvidence],
      ['Review status', profile => profile.label],
      ['Testing limitation', profile => profile.limitation]
    ];"""
js,n = re.subn(r'const fields = \[.*?\n    \];', lambda _:replacement, js, count=1, flags=re.S)
assert n == 1
script.string = js
style = soup.select_one('#card-detail-styles')
if style:
    style.decompose()
style = soup.new_tag('style', id='card-detail-styles')
style.string = """
.offer-evidence-note{font-size:11px;line-height:1.75;color:#5e6d81;margin:0 0 17px;max-width:850px}.offer-evidence-note strong{color:var(--ink)}.offer-evidence-note a,.card-offer-evidence a,.review-offer-note a{color:var(--teal);text-decoration:underline;text-underline-offset:3px}
.card-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin:0;padding:4px 20px 14px;background:#fff}.card-facts>div{min-width:0;padding:11px 12px;border-top:1px solid var(--line);background:#f6f8fb}.card-facts dt{font-size:9px;font-weight:700;letter-spacing:.65px;text-transform:uppercase;color:#748095;margin:0 0 5px}.card-facts dd{font-size:11px;font-weight:600;line-height:1.6;color:#263b56;margin:0;overflow-wrap:anywhere}.card-facts>div:nth-child(3n+2){border-left:1px solid var(--line);border-right:1px solid var(--line)}
.card-offer-evidence{border-top:1px solid var(--line);padding-top:14px;margin-top:15px}.card-offer-evidence ul{padding-left:18px;margin:12px 0}.card-offer-evidence li+li{margin-top:6px}.card-offer-evidence .evidence-date{font-size:10px;color:var(--muted)}.review-offer-note{font-size:12px;line-height:1.8;background:#eef5f3;padding:12px 15px;border-left:3px solid var(--teal);margin-bottom:20px;color:#435f55}
@media(max-width:590px){.card-facts{grid-template-columns:repeat(2,minmax(0,1fr));padding:0 13px 13px}.card-facts>div{padding:10px}.card-facts>div:nth-child(3n+2){border-left:0;border-right:0}.card-facts>div:nth-child(even){border-left:1px solid var(--line)}.card-facts dt{font-size:8px}.card-facts dd{font-size:10px}.offer-evidence-note{font-size:10px}.review-offer-note{font-size:11px;padding:11px 12px}}
"""
soup.head.append(style)

# Earlier reviews described a lack of published numeric offers. Narrow those statements
# where the new panel now supplies attributed information; preserve the remaining review.
replacements = {
 'so an old promotion is not presented here as a November offer.':'so the card labels the available figures as directory reports rather than a confirmed November offer.',
 'No current welcome amount is independently confirmed in this review.':'The card now summarises the indexed operator package; its availability to UK players remains unconfirmed.'
}
for review in content['reviews']:
    for section in review['sections']:
        text=section['text']
        for before,after in replacements.items():
            text=text.replace(before,after)
        section['text']=text
for node in list(soup.select('.review-copy p')):
    for textnode in list(node.find_all(string=True,recursive=False)):
        text=str(textnode)
        for before,after in replacements.items():
            text=text.replace(before,after)
        if text!=str(textnode):
            textnode.replace_with(text)

assert str(soup.find('style')) == original_core_css, 'Core styling changed unexpectedly'
assert original_links == [(a.get('data-affiliate'),a.get('href')) for a in soup.select('a[data-affiliate]')]
assert original_logos == [str(a) for a in soup.select('.casino-card img')]
assert soup.select_one('#overview').find_next_sibling().get('id') == 'casino-reviews'
assert len(soup.select('.card-facts')) == 10
assert len(soup.select('.card-facts dt')) == 60
assert len(soup.select('.casino-review')) == 10
ids=[a['id'] for a in soup.select('[id]')]
assert len(ids)==len(set(ids)), 'Duplicate IDs'
assert all(a['href']=='#' or a['href'][1:] in ids for a in soup.select('a[href^="#"]'))
assert len(soup.select('h1'))==1
assert 'Casino Notes Editorial Team' in soup.select_one('.byline').get_text()
html_path.write_text(str(soup),encoding='utf-8')
content_path.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'content/card-details-november-2026.json').write_text(json.dumps({'retrievedOn':DATE,'method':'Published and indexed sources; not live eligibility or payment testing. UK acceptance is unconfirmed for every entry.','cards':DATA},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'card-update-ui.js').write_text(js,encoding='utf-8')
report={'date':DATE,'reviewPlacement':'Immediately after #overview','cardsWithFacts':10,'factFields':60,'reviews':10,'logosUnchanged':True,'affiliateLinksUnchanged':True,'coreCssUnchanged':True,'duplicateIds':0,'brokenInternalAnchors':0,'ukAcceptance':'Unconfirmed; no affirmative acceptance labels added','htmlSha256':hashlib.sha256(html_path.read_bytes()).hexdigest()}
(ROOT/'card-update-report.json').write_text(json.dumps(report,indent=2)+'\n')
if (ROOT/'CHANGELOG.md').exists():
    with (ROOT/'CHANGELOG.md').open('a',encoding='utf-8') as f:
        f.write('\n\n## Review placement and comparison details — 16 November 2026\n\n- Moved all ten detailed reviews immediately after the non-GamStop explanation, retaining the top comparison cards.\n- Added bonus/spin headlines and six labelled information fields per card, with attributed sources and explicit unresolved eligibility.\n- Kept source currencies, existing logos, affiliate URLs, author and the approved core styling.\n- Updated the comparison dialog and source-data file. No live gambling-account tests or UK-acceptance confirmation are claimed.\n')
if (ROOT/'QA.md').exists():
    with (ROOT/'QA.md').open('a',encoding='utf-8') as f:
        f.write('\n\n## Review order and card-details structural checks — 16 November 2026\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n\nThese are executed structural checks. Browser results, when executed, are recorded separately.\n')
print(json.dumps(report,indent=2))
