#!/usr/bin/env python3
"""Layout regression smoke tests; Chromium emulates geometry, not iOS WebKit."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[1].joinpath("index.html").read_text()
# Set Safari's navigator.standalone flag before the game's own script executes.
HTML = HTML.replace(
    "<script>",
    '<script>Object.defineProperty(navigator,"standalone",{value:true,configurable:true});</script><script>',
    1,
)
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
CASES = [
    ("iPhone 15", 393, 852),
    ("iPhone 15 clipped viewport", 393, 793),
    ("iPhone 15 Pro Max", 430, 932),
    ("iPhone 15 Pro Max clipped viewport", 430, 873),
    ("iPhone 16 Pro Max", 440, 956),
    ("iPhone 16 Pro Max clipped viewport", 440, 894),
    ("iPhone 16 Pro Max landscape", 956, 440),
    ("compact phone", 320, 568),
]

def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for name, width, height in CASES:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    is_mobile=True,
                    has_touch=True,
                    user_agent=UA,
                )
                try:
                    page.set_content(HTML)
                    page.wait_for_timeout(100)
                    metrics = page.evaluate("""() => {
                      const rect = selector => {
                        const r = document.querySelector(selector).getBoundingClientRect();
                        return { top:r.top, bottom:r.bottom, width:r.width, height:r.height };
                      };
                      return {
                        score:rect('.scorebar'), stage:rect('.stage'),
                        board:rect('.board-panel'), controls:rect('.controls'),
                        actions:rect('.actions'),
                        safeTop:getComputedStyle(document.querySelector('.shell')).paddingTop,
                        appHeight:document.querySelector('.shell').getBoundingClientRect().height
                      };
                    }""")
                    score = metrics["score"]
                    stage = metrics["stage"]
                    board = metrics["board"]
                    controls = metrics["controls"]
                    actions = metrics["actions"]
                    if height > width:
                        assert score["top"] >= 64, (name, "score overlaps status bar", metrics)
                    assert board["bottom"] <= stage["bottom"] + 2, (name, "board clipped", metrics)
                    assert abs(board["height"] - board["width"] * 2) < 1, (name, "wrong aspect", metrics)
                    assert controls["bottom"] <= actions["top"] + 1, (name, "buttons collide", metrics)
                    assert actions["bottom"] <= height, (name, "footer clipped", metrics)
                    assert metrics["appHeight"] <= height, (name, "app exceeds viewport", metrics)
                    if name == "iPhone 16 Pro Max":
                        level_card = page.locator(".scorebar .stat").first
                        level_card.click()
                        page.wait_for_timeout(70)
                        level_card.click()
                        page.wait_for_timeout(70)
                        compact = page.evaluate("() => document.querySelector('.scorebar').getBoundingClientRect().top")
                        assert compact < 64, ("compact mode did not activate", compact)
                        level_card.click()
                        page.wait_for_timeout(70)
                        level_card.click()
                        page.wait_for_timeout(70)
                        protected = page.evaluate("() => document.querySelector('.scorebar').getBoundingClientRect().top")
                        assert protected >= 64, ("protected mode did not return", protected)
                    print("PASS", name)
                finally:
                    page.close()
        finally:
            browser.close()

if __name__ == "__main__":
    run()
