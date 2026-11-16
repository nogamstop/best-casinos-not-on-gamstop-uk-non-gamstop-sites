"""Apply the publisher's specified controls, ratings and GBP presentation change.

Run once against the checked November card-details version. Does not fetch or
invent offers. Converted amounts remain clearly labelled indicative equivalents.
"""
from __future__ import annotations
import hashlib
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'dc15ffe8b2eabc5d83a1a7ae09739eba432bd1bde10e8aec635a072cfff28cd8'
IDS = ['donbet','goldenbet','betportal','mystake','wildies','betride','casinok','betfoxx','booming-slots','patrick-spins']
VALUES = [9.8,9.7,9.6,9.2,9.0,8.9,8.8,8.5,8.3,8.0]
RATINGS = dict(zip(IDS, VALUES))
EUR_GBP = Decimal('0.83450')
EUR_USD = Decimal('1.1014')
USD_GBP = EUR_GBP / EUR_USD
RATE_URL = 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html'
NUMBER = r'\d[\d,]*(?:\.\d+)?'


def money(amount: str, rate: Decimal) -> str:
    value = (Decimal(amount.replace(',', '')) * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f'≈£{value:,.2f}'


def convert_text(text: str) -> str:
    # Use an explicitly published GBP amount instead of converting its alternative.
    text = re.sub(r'€' + NUMBER + r'\s*/\s*(£' + NUMBER + r')', r'\1', text)
    # Where two source denominations are offered, display the euro-basis equivalent only.
    text = re.sub(r'(€' + NUMBER + r')\s*(?:/|or)\s*(?:US)?\$' + NUMBER, r'\1', text)
    text = text.replace('€/$', '€')
    # Do not assume that a stablecoin is worth exactly one US dollar.
    text = text.replace('100,000 USDC/week (directory-listed)', 'Crypto limits apply; GBP amount unconfirmed')
    text = text.replace('The directory also reports a 250,000 USDC monthly limit;', 'The directory also reports a separate crypto-denominated monthly limit;')
    text = text.replace('Directory-listed · amount retained in USD', 'Directory-listed · indicative GBP equivalent')
    text = text.replace('We have not combined them into a guaranteed package or converted the amount to pounds.', 'We have not combined them into a guaranteed package. The GBP display is an indicative conversion, not a confirmed pound-denominated offer.')
    text = re.sub(r'€(' + NUMBER + r')', lambda m: money(m.group(1), EUR_GBP), text)
    text = re.sub(r'(?:US)?\$(' + NUMBER + r')', lambda m: money(m.group(1), USD_GBP), text)
    return text


def convert_tree(value):
    if isinstance(value, str):
        if value.startswith(('https://','http://')):
            return value
        # Hypothetical examples use pounds throughout so their arithmetic remains exact.
        if value.startswith('Consider an illustrative €50 qualifying deposit') or 'In a hypothetical example, a 20% deduction from a €100' in value:
            value = value.replace('€', '£')
        value = value.replace('with a minimum qualifying deposit of 30 in the listed currencies', 'with a minimum qualifying deposit equivalent to approximately £25.04 on the same source-currency basis')
        return convert_text(value)
    if isinstance(value, list):
        return [convert_tree(v) for v in value]
    if isinstance(value, dict):
        return {k: convert_tree(v) for k,v in value.items()}
    return value


def main() -> None:
    path = ROOT / 'index.html'
    original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED, 'Source changed: review before applying this one-off patch.'
    soup = BeautifulSoup(original, 'html.parser', from_encoding='utf-8')
    css_before = [n.string for n in soup.find_all('style')]
    original_links = [a['href'] for a in soup.select('[data-affiliate]')]
    assert len(original_links) == 10
    filters = soup.select_one('.list-tools .filters')
    assert filters and len(filters.select('button[data-filter]')) == 3
    filters.decompose()
    caption = soup.select_one('.list-caption > span')
    assert caption and 'Published-information reviews' in caption.get_text()
    caption.decompose()
    soup.select_one('#casino-sort option[value="listed"]')['value'] = 'rating'
    soup.select_one('#casino-sort option[value="rating"]').string = 'Rating: high to low'
    soup.select_one('.list-caption .sr-only').string = 'Sort casinos'
    soup.select_one('#no-results p').string = 'Try another casino name or clear your search.'
    reset = soup.select_one('#reset-filters')
    reset['id'] = 'reset-search'
    reset.clear()
    reset.string = 'Clear search'

    for node in list(soup.find_all(string=True)):
        if node.parent.name in {'script','style'}:
            continue
        old = str(node)
        new = convert_tree(old)
        if new != old:
            node.replace_with(new)
    profiles = convert_tree(json.loads(soup.select_one('#casino-data').string))
    for profile in profiles:
        profile['rating'] = RATINGS[profile['id']]
        profile['ratingSource'] = 'Publisher-assigned editorial score'
    profiles.sort(key=lambda p:p['rating'], reverse=True)
    soup.select_one('#casino-data').string = json.dumps(profiles, ensure_ascii=False)

    for brand, rating in RATINGS.items():
        card = soup.select_one(f'.casino-card[data-brand="{brand}"]')
        card['data-rating'] = f'{rating:.1f}'
        score = card.select_one('.score-placeholder')
        score['class'] = ['score-placeholder','editorial-score']
        score.clear()
        label = soup.new_tag('a', href='#rating-method', attrs={'class':'rating-label'})
        label.string = 'Editorial rating'
        score.append(label)
        number = soup.new_tag('strong', attrs={'class':'rating-value'})
        number.string = f'{rating:.1f}'
        denom = soup.new_tag('span', attrs={'class':'rating-denominator'})
        denom.string = '/10'
        number.append(denom)
        score.append(number)
        review = soup.select_one(f'#review-{brand} .article-heading')
        p = soup.new_tag('p', attrs={'class':'review-rating'})
        a = soup.new_tag('a', href='#rating-method')
        a.string = f'Editorial rating: {rating:.1f}/10'
        p.append(a)
        review.append(p)

    disclosure = soup.select_one('#editorial-disclosure .source-intro')
    disclosure.string = disclosure.get_text().replace(
        'The ten brands were selected by the publisher; their order is not a safety ranking.',
        'The brands and numerical editorial scores were supplied by the publisher. The list is ordered by those scores, which are not independently tested or customer-review averages.')
    about = soup.select_one('#about-dialog .dialog-body > p')
    about.string = 'This page compares ten publisher-selected brands. The numerical scores are publisher-assigned editorial ratings, not independent test results or customer-review averages. Inclusion is not a blanket recommendation.'
    h = soup.new_tag('h4', id='rating-method')
    h.string = 'About the editorial ratings'
    p = soup.new_tag('p', attrs={'class':'source-intro'})
    p.string = 'Scores out of ten are assigned by the site publisher and determine the default order. No independently validated scoring model or first-hand gambling tests support these numbers. Read the documented terms, warnings and limitations for each site; a higher score does not certify safety, licensing or payment reliability.'
    soup.select_one('#editorial-disclosure').append(h)
    soup.select_one('#editorial-disclosure').append(p)

    note = soup.new_tag('p', id='currency-note', attrs={'class':'currency-note'})
    note.append('Amounts marked ≈ are indicative GBP equivalents, not confirmed GBP offers. Calculated using ')
    a = soup.new_tag('a', href=RATE_URL, target='_blank', rel='noopener')
    a.string = 'ECB reference rates dated 16 November 2026'
    note.append(a)
    note.append('. Original-currency terms, eligibility and cashier rates apply; GBP display does not confirm UK availability. Crypto-denominated limits are not assumed to equal cash.')
    soup.select_one('#casino-cards').insert_before(note)

    ui = soup.find_all('script')[-1]
    code = ui.string
    code = code.replace("  const filters = $$('[data-filter]');\n", '')
    code = code.replace("  let activeFilter = 'all';\n", '')
    code = code.replace("      const matchesStatus = activeFilter === 'all' || card.dataset.status === activeFilter;\n", '')
    code = code.replace('card.hidden = !(matchesStatus && matchesName);', 'card.hidden = !matchesName;')
    code = code.replace("    activeFilter = 'all';\n", '')
    code = code.replace("    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === 'all')));\n", '')
    code, count = re.subn(r"  filters\.forEach\(button => button\.addEventListener\('click', \(\) => \{.*?\n  \}\)\);\n", '', code, flags=re.S)
    assert count == 1
    code = code.replace("if (sort.value === 'listed') return profiles.findIndex(p => p.id === a.dataset.brand) - profiles.findIndex(p => p.id === b.dataset.brand);", "if (sort.value === 'rating') return Number(b.dataset.rating) - Number(a.dataset.rating);")
    code = code.replace('applyFilters', 'applySearch').replace('resetFilters', 'resetSearch').replace('#reset-filters','#reset-search')
    code = code.replace('reset filters when a deep-linked card is hidden', 'clear the search when a deep-linked card is hidden')
    code = code.replace("      ['Offer', profile => profile.offer],", "      ['Editorial rating', profile => `${profile.rating.toFixed(1)}/10 (publisher-assigned)`],\n      ['Offer', profile => profile.offer],")
    code = code.replace('Side-by-side research comparison. No live offers, ratings or availability have been verified.', 'Side-by-side comparison. Ratings are publisher-assigned; GBP conversions are indicative. Live offers and eligibility are not independently verified.')
    assert 'activeFilter' not in code and 'filters.forEach' not in code
    ui.string = code
    extra = soup.new_tag('style', id='display-refinement')
    extra.string = '''
/* Keep the approved design; simplify controls and add publisher scores. */
.list-tools{justify-content:flex-end}.list-caption{justify-content:flex-end}
.currency-note{font-size:10px;line-height:1.75;color:#667287;margin:0 0 15px}
.currency-note a{text-decoration:underline;text-underline-offset:2px}
.editorial-score .rating-label{display:block;font-size:10px;font-weight:650;color:#526078;text-decoration:underline;text-underline-offset:2px}
.card-action .editorial-score .rating-value{display:block;font-size:34px;line-height:1.15;letter-spacing:-1px;color:var(--teal);margin-top:4px}
.rating-denominator{font-size:12px;color:#667287;letter-spacing:0;font-weight:500;margin-left:3px}
.review-rating a{font-size:12px;color:var(--teal);font-weight:650;text-decoration:underline;text-underline-offset:3px}
#rating-method{margin-top:18px;font-size:15px;scroll-margin-top:145px}
@media(max-width:590px){.list-tools .search-box{width:100%}.card-action .editorial-score .rating-value{font-size:29px}.currency-note{font-size:9px}}
'''
    soup.head.append(extra)
    assert [n.string for n in soup.find_all('style')][:-1] == css_before
    assert [a['href'] for a in soup.select('[data-affiliate]')] == original_links
    assert soup.select_one('#overview').find_next_sibling('section')['id'] == 'casino-reviews'
    assert len(soup.select('.casino-card')) == len(soup.select('.casino-review')) == 10
    assert not soup.select('[data-filter]')
    visible = ' '.join(str(n) for n in soup.find_all(string=True) if n.parent.name not in {'style','script'})
    assert '€' not in visible and not re.search(r'\bEUR\b|\$\d|\bUSD\b',visible)
    assert 'Published-information reviews' not in visible
    result = str(soup)
    result = result.replace('viewbox=', 'viewBox=').replace('<lineargradient','<linearGradient').replace('</lineargradient','</linearGradient').replace('gradientunits=', 'gradientUnits=')
    path.write_text(result, encoding='utf-8')

    for filename, array_key in [('card-details-november-2026.json','cards'),('reviews-november-2026.json','reviews')]:
        file = ROOT/'content'/filename
        data = convert_tree(json.loads(file.read_text()))
        data['displayCurrency'] = 'GBP'
        data['currencyNote'] = note.get_text(' ', strip=True)
        for entry in data[array_key]:
            entry['rating'] = RATINGS[entry['id']]
            entry['ratingSource'] = 'Publisher-assigned editorial score; not independently tested'
        file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    settings = {
        'modified':'2026-11-16','displayCurrency':'GBP','ratings':RATINGS,
        'ratingBasis':'Scores supplied by the publisher; not an independent audit, testing score or customer average.',
        'conversion':{'date':'2026-11-16','source':RATE_URL,'EUR_GBP':str(EUR_GBP),'EUR_USD':str(EUR_USD),'USD_GBP':str(USD_GBP),'rounding':'Nearest penny; HALF_UP','marker':'≈','dualDenominationPolicy':'Use the euro-basis equivalent when no explicit GBP amount is stated. Preserve explicit GBP alternatives.','cryptoPolicy':'Do not convert stablecoins at assumed dollar parity.'}
    }
    (ROOT/'content'/'display-settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n')
    report = {'htmlSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ratings':RATINGS,'statusFiltersRemoved':True,'captionRemoved':True,'displayCurrency':'GBP','approximateCurrencyMarker':'≈','sourceDate':'2026-11-16','cards':10,'reviews':10,'affiliateLinksPreserved':True,'overviewBeforeReviews':True,'originalCssPreserved':True}
    (ROOT/'display-report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'display-ui.js').write_text(code)
    for filename, entry in [('CHANGELOG.md','\n\n## Display refinement — 16 November 2026\n\nRemoved the three status-filter buttons and the requested list caption. Added the publisher-supplied editorial scores and rating-first sorting. Displayed monetary amounts in GBP, keeping native GBP figures and marking converted amounts as indicative using dated ECB rates. Preserved reviews, warnings, sources, affiliate links and the approved layout.\n'),('QA.md','\n\n## Display refinement — 16 November 2026\n\nExecuted structural checks:\n```json\n'+json.dumps(report,indent=2)+'\n```\n\nBrowser results are recorded separately. These checks do not validate the publisher\'s scores or turn a currency conversion into an operator-confirmed GBP offer.\n')]:
        f=ROOT/filename
        if f.exists(): f.write_text(f.read_text()+entry)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
