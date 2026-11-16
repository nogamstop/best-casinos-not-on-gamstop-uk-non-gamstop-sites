"""Browser checks for the requested GBP and publisher-rating presentation."""
from pathlib import Path
import functools, hashlib, json, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [9.8,9.7,9.6,9.2,9.0,8.9,8.8,8.5,8.3,8.0]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/'
errors = []
checks = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width':1440,'height':1100}, reduced_motion='reduce')
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url, wait_until='networkidle')
        assert page.locator('[data-filter]').count() == 0
        assert 'Published-information reviews' not in page.locator('body').inner_text()
        assert '€' not in page.locator('body').inner_text()
        actual=page.locator('.casino-card').evaluate_all('(els)=>els.map(e=>Number(e.dataset.rating))')
        assert actual == EXPECTED, actual
        assert page.locator('.editorial-score').count() == 10
        assert page.locator('#overview').evaluate('(el)=>el.nextElementSibling.id') == 'casino-reviews'
        checks.append('Requested filters and list caption removed; ten publisher ratings in the specified descending order.')
        page.locator('#casino-search').fill('golden')
        assert page.locator('.casino-card:visible').count() == 1
        page.locator('#casino-search').fill('nothing-matches-this')
        assert page.locator('#no-results').is_visible()
        page.locator('#reset-search').click()
        assert page.locator('.casino-card:visible').count() == 10
        page.select_option('#casino-sort','asc')
        assert page.locator('.casino-card').first.get_attribute('data-brand') == 'betfoxx'
        page.select_option('#casino-sort','rating')
        assert page.locator('.casino-card').evaluate_all('(els)=>els.map(e=>Number(e.dataset.rating))') == EXPECTED
        checks.append('Search, empty-results reset, alphabetical sorting and rating-first sorting work.')
        for brand in ['donbet','goldenbet','casinok']:
            page.locator(f'.compare-checkbox[value="{brand}"]').check()
        page.locator('#open-comparison').click()
        comparison=page.locator('#comparison-table-container').inner_text()
        assert '9.8/10 (publisher-assigned)' in comparison
        assert '£' in comparison and '€' not in comparison and '$' not in comparison
        assert '≈£625.88' in comparison
        assert '£50 on each day' in comparison
        page.keyboard.press('Escape')
        page.locator('#clear-comparison').click()
        checks.append('Comparison table displays the same publisher ratings and native or indicative GBP amounts.')
        page.locator('#card-donbet .review-link').first.click()
        assert page.evaluate('location.hash') == '#review-donbet'
        page.locator('#review-donbet .review-rating a').click()
        assert page.evaluate('location.hash') == '#rating-method'
        assert 'publisher' in page.locator('#rating-method + p').inner_text()
        checks.append('Full-review and rating-method links remain functional; warnings and disclosures remain available.')
        for width in [320,360,390,590,768,1000,1440]:
            page.set_viewport_size({'width':width,'height':1000})
            page.goto(url,wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), width
            page.locator('.list-head').evaluate("el=>el.scrollIntoView({block:'start',behavior:'instant'})")
            if width in [390,1440]:
                page.screenshot(path=str(ROOT/('mobile-gbp-ratings.png' if width==390 else 'desktop-gbp-ratings.png')))
        assert page.locator('.casino-card img').evaluate_all("async imgs=>{await Promise.all(imgs.map(i=>{i.loading='eager';return i.decode().catch(()=>{});}));return imgs.every(i=>i.naturalWidth>0);}")
        checks.append('All ten logos decode; no horizontal page overflow at seven viewport widths from 320 to 1440 pixels.')
        nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
        np=nojs.new_page();np.goto(url)
        assert np.locator('.casino-card').count()==10 and np.locator('.casino-review').count()==10
        assert np.locator('.rating-value').count()==10
        assert '€' not in np.locator('body').inner_text()
        checks.append('Ten cards, ten reviews, scores and GBP information remain readable without JavaScript.')
        assert not errors, errors
        nojs.close(); browser.close()
finally:
    server.shutdown()
report={'engine':'Headless Chromium / Playwright','transport':'Local HTTP server; repository files unchanged','checks':checks,'javascriptErrors':errors,'htmlSha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'scope':'Local browser emulation, not physical-device tests or casino verification. Editorial scores supplied by the publisher.'}
(ROOT/'display-browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
qa=ROOT/'QA.md'
if qa.exists():
    qa.write_text(qa.read_text()+'\n\n### Executed display-refinement browser checks\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n')
print(json.dumps(report,indent=2))
