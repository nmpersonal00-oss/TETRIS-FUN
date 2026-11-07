#!/usr/bin/env python3
"""Offline challenge-mode regressions; never contacts or modifies Supabase."""
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
    """Load a nearly cleared board via local fixture, never through backend APIs."""
    page.evaluate("""({key, lines, score, level}) => {
      const snap=JSON.parse(localStorage.getItem(key));
      snap.board=Array.from({length:20},()=>Array(10).fill(null));
      for(let y=18;y<20;y++)for(let x=0;x<10;x++)
        if(x!==4&&x!==5)snap.board[y][x]='T';
      snap.active={name:'O',shape:[[1,1],[1,1]],x:4,y:0};
      snap.score=score;
      snap.lines=lines;
      snap.level=level;
      snap.checkpointScore=score;
      snap.checkpointLines=lines;
      snap.status='paused';
      localStorage.setItem(key,JSON.stringify(snap));
    }""", {"key": PREFIX + mode, "lines": lines, "score": score, "level": level})
    page.set_content(HTML)
    page.locator("#playButton").click()
    page.keyboard.press("Space")
    page.wait_for_function("""() => {
      const snap=JSON.parse(localStorage.getItem('glow-stack-challenge-v1-' + localStorage.getItem('glow-stack-mode-v1')));
      return snap && snap.score >= 100;
    }""")


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
        page.route("**/*", lambda route: route.abort())
        try:
            page.set_content(HTML)
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
            two_line_setup(page,"lines",lines=4)
            assert page.locator("#level").inner_text()=="2"
            assert slot(page,"lines")["lines"]==6
            assert slot(page,"lines")["score"]==100
            print("PASS Line Ladder advances a level every five lines")

            # Switch to Sprint; replay a saved level-4 state near the 40-line goal.
            pick(page,"sprint")
            assert "SPRINT 40" in page.locator("#challengeHudTitle").inner_text()
            assert slot(page,"sprint")["level"]==1
            two_line_setup(page,"sprint",lines=38,level=4)
            assert page.locator("#overlayTitle").inner_text()=="CHALLENGE COMPLETE"
            assert slot(page,"sprint")["status"]=="won"
            page.set_content(HTML)
            assert page.locator("#overlayTitle").inner_text()=="CHALLENGE COMPLETE"
            assert page.locator("#challengeHudGoal").inner_text().startswith("Completed!")
            print("PASS Sprint has four stages, completion, and saved winner state")

            pick(page,"score")
            two_line_setup(page,"score",score=90)
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
            two_line_setup(page,"nohold",lines=48,level=5)
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
