import os
import glob
import re

html_files = glob.glob(r'd:\ОЧ\Програми\*.html')
results = []

for filepath in html_files:
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Check script tags
    script_open = len(re.findall(r'<script\b', content, re.IGNORECASE))
    script_close = len(re.findall(r'</script>', content, re.IGNORECASE))

    # Check curly braces inside script blocks
    script_blocks = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    braces_diff = 0
    for block in script_blocks:
        b_open = block.count('{')
        b_close = block.count('}')
        braces_diff += (b_open - b_close)

    size_kb = round(os.path.getsize(filepath) / 1024, 1)
    results.append({
        'name': fname,
        'size_kb': size_kb,
        'script_open': script_open,
        'script_close': script_close,
        'braces_diff': braces_diff
    })

print("SUMMARY:")
for r in results:
    print(f"- {r['name']} ({r['size_kb']} KB): Scripts ({r['script_open']}/{r['script_close']}), Braces Diff: {r['braces_diff']}")
