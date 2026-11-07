#!/usr/bin/env python3
"""Offline challenge-mode regressions; never contacts or modifies Supabase."""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text()
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
PREFIX = "glow-stack-challenge-v1-"


def pick(page, mode):
    page.locator("#levelButton").click()
    page.locator("#challengesButton").click()
    assert page.locator("[data-game-mode]").count() == 5
    page.locator('[data-game-mode="' + mode + '"]').click()
    assert page.locator("#menuScreen").is_hidden()
    assert page.evaluate("localStorage.getItem('glow-stack-mode-v1')") == mode


def slot(page, mode):
    return page.evaluate("(key) => JSON.parse(localStorage.getItem(key))", PREFIX + mode)


def two_line_setup(page, mode, lines=0, score=0, level=1):
    """Use a fresh browser page to load a prepared board, avoiding pagehide autosave."""
    snap=slot(page,mode)
    snap["board"]=[[None]*10 for _ in range(20)]
    for y in (18,19):
        for x in range(10):
            if x not in (4,5):
                snap["board"][y][x]="T"
    snap["active"]={"name":"O","shape":[[1,1],[1,1]],"x":4,"y":0}
    snap["score"]=score
    snap["lines"]=lines
    snap["level"]=level
    snap["checkpointScore"]=score
    snap["checkpointLines"]=lines
    snap["status"]="paused"

    # Start a new tab so the old app can safely execute its pagehide save
    # BEFORE the fixture is injected on the new page. Its init script runs
    # before the app and only once per tab (sessionStorage guard).
    next_page=page.context.new_page()
    next_page.route("**/*", lambda route: route.fulfill(
        status=200,content_type="text/html",body=HTML
    ) if route.request.url=="https://glowstack.test/" else route.abort())
    script=(
        "if(!sessionStorage.getItem('__challenge_fixture_once')){"
        + "localStorage.setItem(" + json.dumps(PREFIX+mode) + "," + json.dumps(json.dumps(snap)) + ");"
        + "localStorage.setItem('glow-stack-mode-v1'," + json.dumps(mode) + ");"
        + "sessionStorage.setItem('__challenge_fixture_once','yes');"
        + "}"
    )
    next_page.add_init_script(script=script)
    page.close()
    page=next_page
    page.goto("https://glowstack.test/")
    prepared=slot(page,mode)
    assert prepared["board"][19][0]=="T" and prepared["lines"]==lines,("Fixture did not load",prepared)
    page.locator("#playButton").click()
    page.keyboard.press("Space")
    page.wait_for_timeout(250)
    state=page.evaluate("""() => {
      const key='glow-stack-challenge-v1-' + localStorage.getItem('glow-stack-mode-v1');
      const snap=JSON.parse(localStorage.getItem(key));
      return {
        activeMode:localStorage.getItem('glow-stack-mode-v1'),
        visibleScore:document.querySelector('#score').textContent,
        visibleLevel:document.querySelector('#level').textContent,
        overlayHidden:document.querySelector('#overlay').hidden,
        overlayText:document.querySelector('#overlayTitle').textContent,
        active:snap?.active,
        boardBottom:snap?.board?.slice(-2),
        savedStatus:snap?.status,
        savedScore:snap?.score
      };
    }""")
    assert state["savedScore"]>=100,("Expected two-line clear after Space",state)
    return page

def run():
    speed=re.search(r"function interval\(lvl\)\{return ([^}]+)\}",HTML)
    assert speed, "Gravity curve function missing"
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True)
        page=browser.new_page(
            viewport={"width":393,"height":852},
            screen={"width":393,"height":852},
            is_mobile=True,has_touch=True,user_agent=UA,
        )
        # Provide a stable test-only HTTPS origin so localStorage works.
        # All requests except the in-memory HTML document are aborted.
        page.route("**/*", lambda route: route.fulfill(
            status=200, content_type="text/html", body=HTML
        ) if route.request.url=="https://glowstack.test/" else route.abort())
        try:
            page.goto("https://glowstack.test/")
            rates=page.evaluate("""(expr) => {
              const gravity=new Function('lvl','return '+expr);
              return [1,5,6,10,11,15,16,18,20,101].map(gravity);
            }""",speed.group(1))
            assert rates[0]==rates[1]==1500, rates
            assert rates[2]<rates[1] and rates[2]==rates[3],rates
            assert rates[4]<rates[3] and rates[4]==rates[5],rates
            assert rates[6]<rates[5] and rates[6]==rates[7],rates
            assert 1400<rates[7]<1450, ("Level 18 must remain gentle",rates)
            assert rates[-1]>=1100, ("Gravity should have an accessibility floor",rates)
            print("PASS five-level speed steps remain gentle through level 18")

            classic=page.evaluate("localStorage.getItem('glow-stack-save-v3')")
            pick(page,"lines")
            assert page.locator("#challengeHud").is_visible()
            assert "LINE LADDER" in page.locator("#challengeHudTitle").inner_text()
            assert page.evaluate("localStorage.getItem('glow-stack-save-v3')")==classic
            page=two_line_setup(page,"lines",lines=4)
            assert page.locator("#level").inner_text()=="2"
            assert slot(page,"lines")["lines"]==6
            assert slot(page,"lines")["score"]==100
            print("PASS Line Ladder advances a level every five lines")

            # Switch to Sprint; replay a saved level-4 state near the 40-line goal.
            pick(page,"sprint")
            assert "SPRINT 40" in page.locator("#challengeHudTitle").inner_text()
            assert slot(page,"sprint")["level"]==1
            page=two_line_setup(page,"sprint",lines=38,level=4)
            assert page.locator("#overlayTitle").inner_text()=="CHALLENGE COMPLETE"
            assert slot(page,"sprint")["status"]=="won"
            page.reload()
            assert page.locator("#overlayTitle").inner_text()=="CHALLENGE COMPLETE"
            assert page.locator("#challengeHudGoal").inner_text().startswith("Completed!")
            print("PASS Sprint has four stages, completion, and saved winner state")

            pick(page,"score")
            page=two_line_setup(page,"score",score=90)
            assert page.locator("#level").inner_text()=="2"
            assert page.evaluate("Number(localStorage.getItem('glow-stack-best-v3'))")==0
            assert slot(page,"score")["score"]==190
            print("PASS Score Climb advances without modifying Classic Best")

            pick(page,"nohold")
            before=slot(page,"nohold")
            page.locator("#holdBox").click(force=True)
            after=slot(page,"nohold")
            assert before["held"]==after["held"]==None
            assert page.locator("#holdBox").get_attribute("aria-disabled")=="true"
            assert page.locator("#holdBox .preview-subtitle").inner_text()=="NO HOLD"
            page=two_line_setup(page,"nohold",lines=48,level=5)
            assert page.locator("#overlayTitle").inner_text()=="CHALLENGE COMPLETE"
            print("PASS No-Hold blocks Hold and wins on 50 lines")

            pick(page,"marathon")
            assert page.locator("#challengeHud").is_hidden()
            assert page.evaluate("localStorage.getItem('glow-stack-save-v3')") is not None
            assert page.locator("#level").inner_text()=="1"
            assert page.evaluate("Number(localStorage.getItem('glow-stack-best-v3'))")==0
            # Re-enter Line Ladder and confirm it resumes its own saved progress.
            pick(page,"lines")
            assert page.locator("#level").inner_text()=="2"
            assert slot(page,"lines")["lines"]==6
            print("PASS Classic Marathon data and separate challenge saves survive switching")

            # The challenging screens must also fit the same mobile geometry.
            dimensions=page.evaluate("""() => {
              const stage=document.querySelector('.stage').getBoundingClientRect();
              const board=document.querySelector('.board-panel').getBoundingClientRect();
              const hud=document.querySelector('#challengeHud').getBoundingClientRect();
              return {stage,board,hud};
            }""")
            assert dimensions["board"]["top"]>=dimensions["stage"]["top"]-1
            assert dimensions["board"]["bottom"]<=dimensions["stage"]["bottom"]+1
            print("PASS challenge HUD leaves board layout intact")
        finally:
            page.close()
            browser.close()


if __name__=="__main__":
    run()
