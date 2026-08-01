import re

filepath = r'd:\ОЧ\Програми\Звіт ПБД.html'
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Find all document.getElementById calls
get_ids = set(re.findall(r'document\.getElementById\s*\(\s*["\']([^"\']+)["\']\s*\)', text))
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', text))

print("Total getElementById static IDs in JS:", len(get_ids))
print("Total HTML IDs:", len(html_ids))

missing = []
for gid in get_ids:
    if gid not in html_ids and '${' not in gid:
        missing.append(gid)

print("Missing static IDs:", missing)
