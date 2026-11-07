#!/usr/bin/env python3
"""Regression tests for the touch-first, installed-app layout.
Chromium validates viewport geometry and interactions, not iOS system chrome.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT.joinpath("index.html").read_text()
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
CASES = [
    ("iPhone 15", 393, 852, False),
    ("iPhone 15 with short viewport", 393, 793, False),
    ("iPhone 15 Pro Max", 430, 932, False),
    ("iPhone 15 Pro Max with short viewport", 430, 873, False),
    ("iPhone 16 Pro Max", 440, 956, False),
    ("iPhone 16 Pro Max with short viewport", 440, 894, False),
    ("iPhone 16 Pro Max with safe insets", 440, 956, True),
    ("iPhone 16 Pro Max landscape", 956, 440, False),
    ("compact phone", 320, 568, False),
]

def is_hidden(page, selector):
    return page.locator(selector).evaluate("(e) => e.hidden")

def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        errors = []
        try:
            for name, width, height, inset in CASES:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    is_mobile=True, has_touch=True, user_agent=UA,
                )
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                try:
                    page.set_content(HTML)
                    if inset:
                        # Chromium does not expose real iPhone safe-area insets;
                        # simulate a full-bleed Home Screen viewport with a notch and Home bar.
                        page.add_style_tag(content=".shell{padding-top:62px!important;padding-bottom:34px!important;}")
                    page.wait_for_timeout(150)
                    metrics = page.evaluate("""() => {
                      const rect = selector => {
                        const r = document.querySelector(selector).getBoundingClientRect();
                        return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,
                                width:r.width,height:r.height};
                      };
                      return {shell:rect('.shell'),score:rect('.scorebar'),
                              stage:rect('.stage'),board:rect('.board-panel'),
                              rail:rect('.rail'),hold:rect('#holdBox'),
                              next:rect('#nextOne'),nextCard:rect('.rail .preview-card:first-child'),
                              viewport:[innerWidth,innerHeight]};
                    }""")
                    board, stage, rail = (metrics[k] for k in ("board","stage","rail"))
                    assert not page.locator(".controls").count(), (name,"old controls present")
                    assert not page.locator(".actions").count(), (name,"old action buttons present")
                    assert page.locator("#nextTwo").count()==0, (name,"second next piece present")
                    assert metrics["shell"]["bottom"] <= height+1, (name,"shell outside viewport",metrics)
                    assert metrics["score"]["top"] >= metrics["shell"]["top"], (name,"score clipped",metrics)
                    assert board["top"] >= stage["top"]-1 and board["bottom"] <= stage["bottom"]+1, (name,"board vertical clipping",metrics)
                    assert board["left"] >= stage["left"]-1 and board["right"] < rail["left"], (name,"board overlapping Hold/Next",metrics)
                    assert abs(board["height"]-board["width"]*2)<1, (name,"board aspect ratio",metrics)
                    assert abs(metrics["nextCard"]["top"]-board["top"]) < 3, (name,"Next should align with top of board",metrics)
                    assert abs(metrics["hold"]["bottom"]-board["bottom"]) < 3, (name,"Hold should align with bottom of board",metrics)
                    if inset: assert metrics["score"]["top"] >= 62,(name,"safe area not respected",metrics)

                    # Start, pause by tapping Level, enter empty Challenges,
                    # return to Options, close X and automatically resume.
                    page.locator("#playButton").click()
                    assert is_hidden(page,"#overlay"),(name,"did not start")
                    page.locator("#levelButton").click()
                    assert not is_hidden(page,"#menuScreen"),(name,"menu not opened")
                    assert not is_hidden(page,"#overlay"),(name,"game didn't pause")
                    page.locator("#challengesButton").click()
                    assert not is_hidden(page,"#challengesPage"),(name,"challenges missing")
                    assert is_hidden(page,"#optionsPage"),(name,"options not hidden")
                    page.locator("#menuBack").click()
                    assert not is_hidden(page,"#optionsPage"),(name,"back failed")
                    page.locator("#menuClose").click()
                    assert is_hidden(page,"#menuScreen"),(name,"X did not close")
                    assert is_hidden(page,"#overlay"),(name,"X did not resume")

                    before=page.locator("#held").evaluate("(e) => e.toDataURL()")
                    page.locator("#holdBox").click()
                    after=page.locator("#held").evaluate("(e) => e.toDataURL()")
                    assert before!=after,(name,"Hold did not update held preview")
                    assert "unavailable" in page.locator("#holdBox").get_attribute("class"),(name,"Hold should only be usable once per piece")
                    # Restart current level through menu, play resumes.
                    page.locator("#levelButton").click()
                    page.locator("#restartButton").click()
                    assert is_hidden(page,"#menuScreen") and is_hidden(page,"#overlay"),(name,"restart failed")
                    assert "unavailable" not in page.locator("#holdBox").get_attribute("class"),(name,"Hold not reset")
                    page.locator("#levelButton").click()
                    page.locator("#resetButton").click()
                    assert page.locator("#level").inner_text()=="1",(name,"Level 1 reset failed")
                    assert is_hidden(page,"#overlay"),(name,"Level 1 didn't resume")

                    if name in ("iPhone 15","iPhone 16 Pro Max","iPhone 16 Pro Max with safe insets"):
                        (ROOT / "screenshots").mkdir(exist_ok=True)
                        slug=name.lower().replace(" ","_")
                        page.screenshot(path=str(ROOT/"screenshots"/f"{slug}.png"),full_page=True)
                    print(f"PASS {name} | board {board['width']:.0f} x {board['height']:.0f}; available {stage['height']:.0f}")
                finally:
                    page.close()
            assert not errors,errors
        finally:
            browser.close()

if __name__=="__main__":
    run()
