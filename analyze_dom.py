from playwright.sync_api import sync_playwright
import time
import json

platform = input("Enter platform (instagram/whatsapp/twitter): ")

with sync_playwright() as p:
    session_dir = f'D:/Hackathon-0/Gold-Tier/browser_sessions/{platform}_session'

    if platform == 'instagram':
        url = 'https://www.instagram.com/direct/inbox/'
    elif platform == 'whatsapp':
        url = 'https://web.whatsapp.com/'
    else:
        url = 'https://twitter.com/messages'

    browser = p.chromium.launch_persistent_context(
        user_data_dir=session_dir,
        headless=False
    )
    page = browser.pages[0]
    page.goto(url, wait_until='domcontentloaded')
    time.sleep(8)

    print("\n=== Analyzing DOM Structure ===")

    # Get all clickable elements that might be conversations
    script = """
    () => {
        const results = [];

        // Find all elements with click handlers or links
        const clickables = document.querySelectorAll('a, div[role="button"], div[role="link"], [onclick]');

        for (let elem of clickables) {
            const text = elem.innerText?.trim();
            const href = elem.getAttribute('href');
            const role = elem.getAttribute('role');
            const classes = elem.className;
            const testid = elem.getAttribute('data-testid');

            // Only include elements with meaningful text
            if (text && text.length > 0 && text.length < 200) {
                results.push({
                    text: text.substring(0, 100),
                    tag: elem.tagName,
                    role: role,
                    href: href,
                    classes: classes,
                    testid: testid
                });
            }
        }

        return results.slice(0, 20);  // First 20 results
    }
    """

    elements = page.evaluate(script)

    print(f"\nFound {len(elements)} potential conversation elements:\n")

    for i, elem in enumerate(elements, 1):
        print(f"{i}. Text: {elem['text'][:50]}")
        print(f"   Tag: {elem['tag']}, Role: {elem['role']}")
        if elem['href']:
            print(f"   Href: {elem['href']}")
        if elem['testid']:
            print(f"   TestID: {elem['testid']}")
        if elem['classes']:
            print(f"   Classes: {elem['classes'][:100]}")
        print()

    # Save to file
    with open(f'{platform}_dom_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(elements, f, indent=2)
    print(f"\nSaved detailed analysis to {platform}_dom_analysis.json")

    input("\nPress Enter to close...")
