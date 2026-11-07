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
    ("iPhone 15 installed app", 393, 852, True),
    ("iPhone 15 Pro Max installed app", 430, 932, True),
    ("iPhone 16 Pro Max installed app", 440, 956, True),
    ("iPhone 15 installed app with short viewport", 393, 793, True),
    ("iPhone 16 Pro Max installed app with short viewport", 440, 894, True),
    ("iPhone 16 Pro Max installed app with tall island", 440, 894, True),
    ("compact iPhone installed app", 320, 568, True),
    ("iPhone 16 Pro Max landscape", 956, 440, False),
    ("compact phone", 320, 568, False),
]

def is_hidden(page, selector):
    return page.locator(selector).evaluate("(e) => e.hidden")

def isolated_page(browser, **kwargs):
    """Never allow UI tests to reach live Supabase or other network APIs.

    Earlier viewport tests opened Leaderboard on many simulated phones, which
    unintentionally made anonymous sign-in calls against the production
    Supabase project. Every browser page now blocks outbound network requests
    before app HTML loads; mock tests supply fake Supabase APIs explicitly.
    """
    page = browser.new_page(**kwargs)
    page.route("**/*", lambda route: route.abort())
    return page

def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        errors = []
        try:
            for name, width, height, inset in CASES:
                page = isolated_page(browser,
                    viewport={"width": width, "height": height},
                    is_mobile=True, has_touch=True, user_agent=UA,
                )
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                try:
                    page.set_content(HTML)
                    if inset:
                        # Chromium cannot emulate iOS system chrome, but explicitly
                        # exercise the CSS fallback for navigator.standalone used on
                        # iOS Home Screen apps when display-mode media is unreliable.
                        page.evaluate("document.documentElement.classList.add('ios-home-screen')")
                        if "tall island" in name:
                            # Stress layout when iOS reserves even more top space.
                            page.add_style_tag(content="html.ios-home-screen .shell{padding-top:88px!important;}")
                    page.wait_for_timeout(150)
                    metrics = page.evaluate("""() => {
                      const rect = selector => {
                        const r = document.querySelector(selector).getBoundingClientRect();
                        return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,
                                width:r.width,height:r.height};
                      };
                      return {shell:rect('.shell'),score:rect('.scorebar'),
                              stage:rect('.stage'),board:rect('.board-panel'),
                              hold:rect('#holdBox'),
                              next:rect('#nextOne'),nextCard:rect('.next-top'),
                              nextLabel:rect('.next-top .preview-label'),
                              paddingBottom:parseFloat(getComputedStyle(document.querySelector('.shell')).paddingBottom),
                              paddingTop:parseFloat(getComputedStyle(document.querySelector('.shell')).paddingTop),
                              viewport:[innerWidth,innerHeight]};
                    }""")
                    board, stage, hold = (metrics[k] for k in ("board","stage","hold"))
                    assert not page.locator(".controls").count(), (name,"old controls present")
                    assert not page.locator(".actions").count(), (name,"old action buttons present")
                    assert page.locator("#nextTwo").count()==0, (name,"second next piece present")
                    assert metrics["shell"]["bottom"] <= height+1, (name,"shell outside viewport",metrics)
                    assert metrics["score"]["top"] >= metrics["shell"]["top"], (name,"score clipped",metrics)
                    assert board["top"] >= stage["top"]-1 and board["bottom"] <= stage["bottom"]+1, (name,"board vertical clipping",metrics)
                    assert board["left"] >= stage["left"]-1 and board["right"] <= stage["right"]+1, (name,"board horizontal clipping",metrics)
                    assert abs(board["height"]-board["width"]*1.86)<1, (name,"board presentation ratio",metrics)
                    assert metrics["paddingBottom"]<=3,(name,"unwanted bottom padding",metrics)
                    assert metrics["score"]["height"]<=64, (name,"top stats too tall",metrics)
                    assert abs(metrics["nextCard"]["top"]-metrics["score"]["top"])<2, (name,"Next not in top bar",metrics)
                    assert metrics["nextCard"]["bottom"]<=metrics["score"]["bottom"]+1,(name,"Next overflows header",metrics)
                    assert metrics["nextLabel"]["top"]>=metrics["nextCard"]["top"]+1, (name,"Next text overflows header",metrics)
                    assert metrics["next"]["bottom"]<=metrics["nextCard"]["bottom"]-1,(name,"Next block clipped by header",metrics)
                    assert hold["height"]<=65, (name,"Hold too tall",metrics)
                    assert hold["top"]>=stage["bottom"]-1,(name,"Hold collides with board",metrics)
                    assert abs(hold["width"]-board["width"])<=1, (name,"Hold width not aligned with board",metrics)
                    assert hold["bottom"]<=metrics["shell"]["bottom"]+1, (name,"Hold clipped offscreen",metrics)
                    if height>width and width>=360:
                        # On a SHORT standalone viewport, preserving the 76px
                        # Dynamic Island tap-safe zone takes priority over the
                        # old 84%-width target. The board should still fill the
                        # space left by the status bar, stats and Hold control.
                        min_width_fraction=.80 if inset and "short viewport" in name else (.83 if "tall island" in name else .84)
                        assert board["width"]>=min_width_fraction*width, (name,"board too skinny",metrics)
                        assert stage["height"]-board["height"]<=60, (name,"board not using available height",metrics)
                    if inset:
                        safe_clock=88 if "tall island" in name else 76
                        assert metrics["paddingTop"] >= safe_clock,(name,"missing iPhone clock clearance",metrics)
                        assert metrics["score"]["top"] >= safe_clock,(name,"top buttons under Dynamic Island",metrics)
                        assert metrics["score"]["bottom"]>safe_clock+40,(name,"top controls not tappable",metrics)

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
                    page.locator("#levelButton").click()
                    page.locator("#leaderboardButton").click()
                    assert not is_hidden(page,"#leaderboardPage"),(name,"leaderboard missing")
                    assert is_hidden(page,"#optionsPage"),(name,"options still shown")
                    assert page.locator(".trophy-hero img").count()==1,(name,"trophy illustration missing")
                    page.locator("#menuBack").click()
                    page.locator("#menuClose").click()
                    assert is_hidden(page,"#overlay"),(name,"leaderboard X did not resume")

                    before=page.locator("#held").evaluate("(e) => e.toDataURL()")
                    page.locator("#holdBox").click()
                    after=page.locator("#held").evaluate("(e) => e.toDataURL()")
                    assert before!=after,(name,"Hold did not update held preview")
                    assert "unavailable" in page.locator("#holdBox").get_attribute("class"),(name,"Hold should only be usable once per piece")
                    assert page.locator("#holdBox").evaluate("(e)=>getComputedStyle(e).opacity")=="1",(name,"Held piece faded after use")
                    assert page.locator("#holdBox .preview-subtitle").inner_text()=="WAIT FOR NEXT",(name,"Hold cooldown label missing")
                    # Verify that Hold has large, visible blocks IN the canvas,
                    # not merely a wider blank space around a tiny shape.
                    held_pixels=page.locator("#held").evaluate("""e=>{
                      const c=e.getContext('2d'),w=e.width,h=e.height;
                      const pix=c.getImageData(0,0,w,h).data;
                      let minX=w,maxX=-1,minY=h,maxY=-1;
                      for(let y=0;y<h;y++)for(let x=0;x<w;x++){
                        const i=(y*w+x)*4;
                        if(pix[i+3]>70){
                          minX=Math.min(minX,x);maxX=Math.max(maxX,x);
                          minY=Math.min(minY,y);maxY=Math.max(maxY,y);
                        }
                      }
                      const r=e.getBoundingClientRect();
                      return [(maxX-minX+1)*r.width/w,(maxY-minY+1)*r.height/h,r.width,r.height];
                    }""")
                    assert held_pixels[0]>=36 and held_pixels[1]>=26,(name,"Held piece remains too small",held_pixels)
                    if name in ("iPhone 16 Pro Max installed app",):
                        (ROOT / "screenshots").mkdir(exist_ok=True)
                        page.screenshot(path=str(ROOT / "screenshots" / "iphone_16_pro_max_with_held_piece.png"),full_page=True)
                    # Restart current level through menu, play resumes.
                    page.locator("#levelButton").click()
                    page.locator("#restartButton").click()
                    assert is_hidden(page,"#menuScreen") and is_hidden(page,"#overlay"),(name,"restart failed")
                    assert "unavailable" not in page.locator("#holdBox").get_attribute("class"),(name,"Hold not reset")
                    page.locator("#levelButton").click()
                    page.locator("#resetButton").click()
                    assert page.locator("#level").inner_text()=="1",(name,"Level 1 reset failed")
                    assert is_hidden(page,"#overlay"),(name,"Level 1 didn't resume")

                    if name in ("iPhone 15","iPhone 16 Pro Max","iPhone 16 Pro Max installed app"):
                        (ROOT / "screenshots").mkdir(exist_ok=True)
                        slug=name.lower().replace(" ","_")
                        page.screenshot(path=str(ROOT/"screenshots"/f"{slug}.png"),full_page=True)
                    print(f"PASS {name} | board {board['width']:.0f} x {board['height']:.0f}; available {stage['height']:.0f}")
                finally:
                    page.close()
            # Mock the Supabase network to verify actual username and ranking UI.
            # Live database RLS and SQL checks are verified separately.
            mock_page=isolated_page(browser,viewport={"width":440,"height":956},is_mobile=True,has_touch=True,user_agent=UA)
            try:
                mock_page.set_content(HTML)
                mock_page.evaluate("""() => {
                  window.__players=[{user_id:'husband',username:'Hubby',best_score:500,current_level:4}];
                  window.__anonymousSignIns=0;
                  window.supabase={createClient:()=>({
                    auth:{
                      getSession:async()=>({data:{session:null},error:null}),
                      signInAnonymously:async()=>{
                        window.__anonymousSignIns++;
                        return {data:{session:{user:{id:'wife'}}},error:null};
                      }
                    },
                    from:()=>({
                      filter:null,updated:null,
                      select(){return this;},
                      eq(_,value){this.filter=value;return this;},
                      maybeSingle:async()=>({data:null,error:null}),
                      async upsert(p){
                        let row=window.__players.find(x=>x.user_id===p.user_id);
                        if(row){row.username=p.username;row.best_score=Math.max(row.best_score,p.best_score);row.current_level=p.current_level}
                        else window.__players.push({...p});
                        return {error:null};
                      },
                      update(p){this.updated=p;return this;},
                      async single(){
                        const row=window.__players.find(x=>x.user_id===this.filter);
                        row.best_score=Math.max(row.best_score,this.updated.best_score);
                        row.current_level=this.updated.current_level;
                        return {data:{best_score:row.best_score,current_level:row.current_level},error:null};
                      },
                      order(){return this;},
                      async limit(){
                        return {data:[...window.__players].sort((a,b)=>b.best_score-a.best_score),error:null};
                      }
                    })
                  })}
                }""")
                mock_page.locator("#levelButton").click()
                mock_page.locator("#leaderboardButton").click()
                assert mock_page.locator(".trophy-hero strong").inner_text()=="TETRIS CHAMPIONS","Leaderboard title incorrect"
                mock_page.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('tap Save Name')")
                assert mock_page.evaluate("window.__anonymousSignIns")==0,"Opening Leaderboard created an unwanted anonymous account"
                assert mock_page.locator("#leaderboardList .board-person").count()==0,"New player should have no registered identity"
                mock_page.locator("#playerNameInput").fill("Wifey")
                mock_page.locator("#savePlayerButton").click()
                mock_page.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('Playing as Wifey')")
                assert mock_page.evaluate("window.__anonymousSignIns")==1,"Saving a name should create exactly one anonymous account"
                assert mock_page.locator("#leaderboardList .board-person").all_inner_texts()==["Hubby","Wifey"],"Initial ranking failed"
                assert mock_page.locator("#leaderboardList .board-player-level").all_inner_texts()==["LEVEL 4","LEVEL 1"],"Player levels missing from leaderboard"
                assert mock_page.locator("#leaderboardList .board-points").all_inner_texts()==["500","0"],"Best scores missing from leaderboard"
                # Simulate a higher online high score and a later level on the wife's phone.
                mock_page.evaluate("""() => {
                  window.__players.find(x=>x.username==='Wifey').best_score=800;
                  window.__players.find(x=>x.username==='Wifey').current_level=6;
                }""")
                mock_page.locator("#menuBack").click()
                mock_page.locator("#leaderboardButton").click()
                mock_page.wait_for_function("() => document.querySelector('#leaderboardList .board-person')?.textContent==='Wifey'")
                assert mock_page.locator("#leaderboardList .board-person").all_inner_texts()==["Wifey","Hubby"],"High score did not change ranks"
                assert mock_page.locator("#leaderboardList .board-player-level").all_inner_texts()==["LEVEL 6","LEVEL 4"],"Updated current levels not shown"
                assert mock_page.locator("#leaderboardList .board-points").all_inner_texts()==["800","500"],"Updated best scores not shown"
                mock_page.locator("#menuBack").click()
                mock_page.locator("#challengesButton").click()
                mock_page.wait_for_function("() => document.querySelector('#challengeProgressList .challenge-numbers strong')?.textContent==='LEVEL 6'")
                assert mock_page.locator("#challengeProgressList .challenge-player").all_inner_texts()==["Wifey","Hubby"],"Challenges should compare both players"
                assert mock_page.locator("#challengeProgressList .challenge-numbers strong").all_inner_texts()==["LEVEL 6","LEVEL 4"],"Challenges does not show current levels"
                assert "Best 800" in mock_page.locator("#challengeProgressList").inner_text(),"Challenges should show best score"
                assert mock_page.evaluate("window.__anonymousSignIns")==1,"Browsing Challenges must not add anonymous accounts"
                mock_page.locator("#menuClose").click()
                assert is_hidden(mock_page,"#menuScreen"),"Challenges could not close"
                print("PASS shared leaderboard mock | no-email username setup, best scores and current levels in both views")
            finally:
                mock_page.close()
            # The owner must enable this in the Supabase Dashboard. If it's off,
            # the app must report a clear one-time setup step and retain the typed name.
            disabled_page=isolated_page(browser,viewport={"width":440,"height":956},is_mobile=True,has_touch=True,user_agent=UA)
            try:
                disabled_page.set_content(HTML)
                disabled_page.evaluate("""() => {
                  window.supabase={createClient:()=>({
                    auth:{
                      getSession:async()=>({data:{session:null},error:null}),
                      signInAnonymously:async()=>({data:{session:null},error:{message:'Anonymous sign-ins are disabled'}})
                    }
                  })}
                }""")
                disabled_page.locator("#levelButton").click()
                disabled_page.locator("#leaderboardButton").click()
                disabled_page.locator("#playerNameInput").fill("Wifey")
                disabled_page.locator("#savePlayerButton").click()
                disabled_page.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('Supabase is rejecting anonymous sign-ins')")
                status=disabled_page.locator("#boardStatus").inner_text()
                assert "Authentication" in status and "Providers" in status, status
                assert "reload that settings page" in status, status
                assert disabled_page.locator("#playerNameInput").input_value()=="Wifey","Name lost after error"
                print("PASS anonymous provider disabled | actionable setup message, name retained")
            finally:
                disabled_page.close()
            # CAPTCHA-required errors must not be mistaken for a disabled provider.
            captcha_page=isolated_page(browser,viewport={"width":440,"height":956},is_mobile=True,has_touch=True,user_agent=UA)
            try:
                captcha_page.set_content(HTML)
                captcha_page.evaluate("""() => {
                  window.supabase={createClient:()=>({
                    auth:{
                      getSession:async()=>({data:{session:null},error:null}),
                      signInAnonymously:async()=>({data:{session:null},error:{code:'captcha_failed',message:'Captcha verification required for anonymous signup'}})
                    }
                  })}
                }""")
                captcha_page.locator("#levelButton").click()
                captcha_page.locator("#leaderboardButton").click()
                captcha_page.locator("#playerNameInput").fill("Wifey")
                captcha_page.locator("#savePlayerButton").click()
                captcha_page.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('requires CAPTCHA')")
                captcha_status=captcha_page.locator("#boardStatus").inner_text()
                assert "Authentication" in captcha_status and "Protection" in captcha_status, captcha_status
                assert "sign-ins are disabled" not in captcha_status, captcha_status
                print("PASS captcha required | distinct guidance without false provider-disabled claim")
            finally:
                captcha_page.close()
            # A pre-existing LOCAL 4,960 record must sync on the FIRST save
            # of a new username, despite the current game score still being 0.
            # Inject a saved best before the startup script runs (the game uses
            # best loaded from the v3 save key in real iOS Home Screen sessions).
            existing_best_html=HTML.replace(
                "if(!load())fresh();refresh();fit();requestAnimationFrame(frame);",
                "if(!load())fresh();best=Math.max(best,4960);refresh();fit();requestAnimationFrame(frame);"
            )
            assert existing_best_html!=HTML,"Could not construct prior-best regression"
            new_player=isolated_page(browser,viewport={"width":440,"height":956},is_mobile=True,has_touch=True,user_agent=UA)
            try:
                new_player.set_content(existing_best_html)
                new_player.evaluate("""() => {
                  window.__players=[];
                  window.supabase={createClient:()=>({
                    auth:{
                      getSession:async()=>({data:{session:null},error:null}),
                      signInAnonymously:async()=>({data:{session:{user:{id:'wife'}}},error:null})
                    },
                    from:()=>({
                      filter:null,
                      select(){return this;},
                      eq(_,id){this.filter=id;return this;},
                      maybeSingle:async()=>({data:null,error:null}),
                      async upsert(p){window.__players=[{...p}];return {error:null}},
                      order(){return this;},
                      async limit(){return {data:window.__players,error:null}}
                    })
                  })}
                }""")
                assert new_player.locator("#best").inner_text()=="4,960","Saved high score not visible"
                assert new_player.locator("#score").inner_text()=="0","Current run is not a fresh game"
                new_player.locator("#levelButton").click()
                new_player.locator("#leaderboardButton").click()
                new_player.locator("#playerNameInput").fill("Wifey")
                new_player.locator("#savePlayerButton").click()
                new_player.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('Playing as Wifey')")
                actual=new_player.evaluate("window.__players[0].best_score")
                assert actual==4960,("New user did not import saved high score",actual)
                assert new_player.locator("#leaderboardList .board-points").first.inner_text()=="4,960","New player leaderboard best wrong"
                print("PASS saved best sync on registration | 4,960 preserved when score is 0")
            finally:
                new_player.close()

            # Existing Supabase player with ONLINE best 120 and LOCAL best 4,960:
            # the game must upload 4,960, never overwrite it with 120, and
            # maintain the correct Best tile and level after a new game.
            old_player=isolated_page(browser,viewport={"width":440,"height":956},is_mobile=True,has_touch=True,user_agent=UA)
            try:
                old_player.set_content(existing_best_html)
                old_player.evaluate("""() => {
                  window.__online={user_id:'wife',username:'Wifey',best_score:120,current_level:1};
                  window.supabase={createClient:()=>({
                    auth:{getSession:async()=>({data:{session:{user:{id:'wife'}}},error:null})},
                    from:()=>({
                      filter:null,updated:null,
                      select(){return this;},
                      eq(_,id){this.filter=id;return this;},
                      maybeSingle:async()=>({data:{...window.__online},error:null}),
                      update(p){this.updated=p;return this;},
                      async single(){
                        window.__online.best_score=Math.max(window.__online.best_score,this.updated.best_score);
                        window.__online.current_level=this.updated.current_level;
                        return {data:{best_score:window.__online.best_score,current_level:window.__online.current_level},error:null};
                      },
                      order(){return this;},
                      async limit(){return {data:[window.__online],error:null}}
                    })
                  })}
                }""")
                old_player.locator("#levelButton").click()
                old_player.locator("#leaderboardButton").click()
                old_player.wait_for_function("() => document.querySelector('#boardStatus').textContent.includes('Playing as Wifey')")
                old_player.wait_for_function("() => window.__online.best_score===4960")
                assert old_player.locator("#best").inner_text()=="4,960","Device Best changed incorrectly"
                old_player.locator("#menuBack").click()
                old_player.locator("#resetButton").click()
                assert old_player.locator("#score").inner_text()=="0","Restart did not reset the current run"
                assert old_player.locator("#best").inner_text()=="4,960","Restart incorrectly reset personal best"
                assert old_player.evaluate("window.__online.best_score")==4960,"Online best decreased after restart"
                print("PASS existing account backfill | Supabase 120 upgraded to local 4,960 and survives restart")
            finally:
                old_player.close()
            assert not errors,errors
        finally:
            browser.close()

if __name__=="__main__":
    run()
