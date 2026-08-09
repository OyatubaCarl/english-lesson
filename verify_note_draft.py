from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    pg = None
    for x in ctx.pages:
        try:
            if "note.com/notes" in x.url or "editor.note.com" in x.url:
                pg = x
                break
        except Exception:
            pass
    if pg is None:
        pg = ctx.pages[0]
    pg.bring_to_front()
    pg.wait_for_timeout(800)
    pg.screenshot(path="/tmp/note_draft_check.png")
    print("URL:", pg.url)
    print("TITLE:", pg.title())
