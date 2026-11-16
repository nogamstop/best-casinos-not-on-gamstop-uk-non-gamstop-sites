"""Functional and responsive checks; no gambling accounts or external clicks."""
import json
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
server = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
checks = []
errors = []
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width':1440,'height':1000}, reduced_motion='reduce')
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8765/', wait_until='networkidle')
        page.locator('.supplied-logo img').evaluate_all('(images) => images.forEach(img => img.loading="eager")')
        page.wait_for_function('Array.from(document.querySelectorAll(".supplied-logo img")).every(img => img.complete && img.naturalWidth > 0)')
        assert page.locator('.casino-card').count() == 10
        assert page.locator('.casino-review').count() == 10
        assert page.locator('.byline').inner_text().startswith('CN\nBy Casino Notes Editorial Team') or 'By Casino Notes Editorial Team' in page.locator('.byline').inner_text()
        checks.append('Ten cards, ten reviews, ten decoded supplied logos and the requested byline.')
        page.locator('[data-filter="warning"]').click()
        assert page.locator('.casino-card:visible').count() == 4
        page.locator('#casino-search').fill('betfoxx')
        assert page.locator('.casino-card:visible').count() == 1
        page.locator('#casino-search').fill('nonexistent-name')
        assert page.locator('#no-results').is_visible()
        page.locator('#reset-filters').click()
        assert page.locator('.casino-card:visible').count() == 10
        checks.append('Status filters, combined search, no-result state and reset.')
        page.locator('#casino-sort').select_option('asc')
        assert page.locator('.casino-card').first.get_attribute('data-brand') == 'betfoxx'
        page.locator('#casino-sort').select_option('listed')
        assert page.locator('.casino-card').first.get_attribute('data-brand') == 'donbet'
        checks.append('Alphabetical sorting and restoration of the publisher-selected order.')
        inputs = page.locator('.compare-checkbox')
        for i in range(3):
            inputs.nth(i).check(force=True)
        inputs.nth(3).check(force=True)
        assert page.locator('.compare-checkbox:checked').count() == 3
        page.locator('#open-comparison').click()
        assert page.locator('#comparison-dialog').is_visible()
        assert page.locator('.compare-table thead th').count() == 4
        page.keyboard.press('Escape')
        assert not page.locator('#comparison-dialog').is_visible()
        page.locator('#clear-comparison').click()
        checks.append('Three-site comparison limit, populated comparison table and Escape dismissal.')
        page.locator('#card-donbet .card-action .review-link').click()
        assert page.url.endswith('#review-donbet')
        page.locator('#review-donbet .review-sources summary').click()
        assert page.locator('#review-donbet .review-sources').get_attribute('open') is not None
        page.locator('.faq-item summary').first.click()
        assert page.locator('.faq-item').first.get_attribute('open') is not None
        checks.append('Internal full-review navigation, source disclosure and FAQ.')
        (root/'previews').mkdir(exist_ok=True)
        for width in (320,360,390,590,768,1000,1440):
            page.set_viewport_size({'width':width,'height':1000})
            page.evaluate('window.scrollTo(0,0)')
            page.wait_for_timeout(100)
            dims=page.evaluate('({scroll:document.documentElement.scrollWidth, width:window.innerWidth})')
            assert dims['scroll'] <= dims['width'] + 1, f'Horizontal overflow at {width}: {dims}'
            if width in (390,1440):
                page.screenshot(path=str(root/'previews'/f'november-{width}.png'))
        checks.append('No document-level horizontal overflow at 320, 360, 390, 590, 768, 1000 and 1440 pixels.')
        page.set_viewport_size({'width':390,'height':844})
        page.locator('.menu-toggle').click()
        assert page.locator('#primary-navigation').is_visible()
        page.locator('#primary-navigation a').first.click()
        assert page.locator('.menu-toggle').get_attribute('aria-expanded') == 'false'
        checks.append('Mobile navigation opens and closes after choosing a section.')
        fallback=browser.new_page(java_script_enabled=False, viewport={'width':390,'height':844})
        fallback.goto('http://127.0.0.1:8765/',wait_until='networkidle')
        assert fallback.locator('.casino-card:visible').count()==10
        assert fallback.locator('.casino-review:visible').count()==10
        checks.append('All ten cards and full reviews remain readable without JavaScript.')
        assert not errors, errors
        checks.append('No browser JavaScript errors during these checks.')
        browser.close()
    report={'engine':'Headless Chromium / Playwright 1.56.0','checks':checks,'javascriptErrors':errors,'limits':'Local browser emulation only. Not physical-device, Safari, Firefox, accessibility certification or real-money operator testing.'}
    (root/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    with (root/'QA.md').open('a') as f:
        f.write('\n\n## Executed browser checks for the November update\n\n'+json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
finally:
    server.terminate()
    server.wait(timeout=10)
