"""Browser checks for the card-details update; no external gambling interaction."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json, shutil
from playwright.sync_api import sync_playwright

ROOT = Path.cwd()
class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/'
errors, checks = [], []
try:
    with sync_playwright() as p:
        executable = shutil.which('chromium')
        browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1080}, reduced_motion='reduce')
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(url, wait_until='load')
        assert page.locator('.card-facts').count() == 10
        assert page.locator('.card-facts dt').count() == 60
        assert page.locator('.casino-review').count() == 10
        assert page.evaluate("document.querySelector('#overview').nextElementSibling.id") == 'casino-reviews'
        assert page.locator('.toc a').nth(1).get_attribute('href') == '#overview'
        assert page.locator('.toc a').nth(2).get_attribute('href') == '#casino-reviews'
        page.evaluate("document.querySelectorAll('.casino-card img').forEach(i=>i.loading='eager')")
        page.wait_for_function("Array.from(document.querySelectorAll('.casino-card img')).every(i=>i.complete&&i.naturalWidth>0)")
        checks.append('Ten cards, 60 facts, ten original logos and ten full reviews; reviews directly follow the overview.')
        page.screenshot(path=str(ROOT/'desktop-cards.png'))
        page.locator('#casino-search').fill('golden')
        assert page.locator('.casino-card:visible').count() == 1
        page.locator('#casino-search').fill('')
        page.locator('#casino-sort').select_option('asc')
        assert page.locator('.casino-card').first.get_attribute('data-brand') == 'betfoxx'
        page.locator('#casino-sort').select_option('listed')
        assert page.locator('.casino-card').first.get_attribute('data-brand') == 'donbet'
        page.locator('.compare-checkbox[value="donbet"]').check()
        page.locator('.compare-checkbox[value="goldenbet"]').check()
        page.locator('#open-comparison').click()
        assert page.locator('#comparison-dialog').is_visible()
        modal = page.locator('#comparison-table-container').inner_text()
        assert '150% up to €750' in modal and '200 free spins' in modal and 'UK players' in modal
        assert 'Free spins' in modal and 'Wagering' in modal and 'Withdrawal / cashout' in modal
        page.screenshot(path=str(ROOT/'comparison.png'))
        page.keyboard.press('Escape')
        page.locator('#clear-comparison').click()
        checks.append('Search, sorting and the comparison modal show the new offer, spins, wagering, UK and payment fields.')
        page.locator('#card-donbet .review-link').first.click()
        page.wait_for_timeout(100)
        assert page.url.endswith('#review-donbet')
        page.locator('#review-donbet a[href="#offer-source-donbet"]').click()
        page.wait_for_timeout(100)
        assert page.locator('#donbet-note').get_attribute('open') is not None
        page.locator('#donbet-note summary').click()
        checks.append('Read-review links and linked offer sources navigate correctly and reveal the collapsed source notes.')
        for width in [320, 360, 390, 590, 768, 1000, 1440]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(url, wait_until='load')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), f'Overflow at {width}'
        checks.append('No document-level horizontal overflow at 320, 360, 390, 590, 768, 1000 and 1440 pixels.')
        page.set_viewport_size({'width': 390, 'height': 1100})
        page.goto(url, wait_until='load')
        page.screenshot(path=str(ROOT/'mobile-cards.png'))
        page.locator('.menu-toggle').click()
        page.locator('#primary-navigation a[href="#overview"]').click()
        assert page.locator('.menu-toggle').get_attribute('aria-expanded') == 'false'
        checks.append('The mobile menu closes after choosing a section.')
        page.set_viewport_size({'width': 1440, 'height': 1080})
        page.goto(url+'#overview', wait_until='load')
        page.wait_for_timeout(100)
        page.screenshot(path=str(ROOT/'overview-reviews.png'))
        context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 1000})
        nojs = context.new_page()
        nojs.goto(url, wait_until='load')
        assert nojs.locator('.card-facts').count() == 10 and nojs.locator('.casino-review').count() == 10
        checks.append('The expanded card information and all reviews remain in the initial HTML and readable without JavaScript.')
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
report = {'engine': 'Headless Chromium via Playwright', 'checks': checks, 'javascriptErrors': errors, 'scope': 'Local browser emulation only; not physical-device, cross-browser, real-money or operator-eligibility testing.'}
(ROOT/'card-browser-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
if (ROOT/'QA.md').exists():
    with (ROOT/'QA.md').open('a', encoding='utf-8') as f:
        f.write('\n\n### Executed card-update browser checks\n\n```json\n'+json.dumps(report, indent=2)+'\n```\n')
print(json.dumps(report, indent=2))
