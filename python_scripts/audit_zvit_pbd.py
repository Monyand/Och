import re

filepath = r'd:\ОЧ\Програми\Звіт ПБД.html'
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    full_text = f.read()

lines = full_text.split('\n')
print(f"Total lines: {len(lines)}")

# 1. External scripts
ext_scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', full_text)
print("External scripts:", ext_scripts)

# 2. Check element IDs defined in HTML vs referenced in JS
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', full_text))

js_get_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', full_text))
js_query_ids = set(re.findall(r'querySelector\(["\']#([^"\']+)["\']\)', full_text))
js_used_ids = js_get_ids.union(js_query_ids)

missing_in_html = js_used_ids - html_ids
# Filter dynamic template IDs if any (containing ${ or +)
static_missing = [m for m in missing_in_html if '${' not in m and '+' not in m]
print("JS references static IDs not found in HTML:", static_missing)

# 3. Check JS functions count
func_defs = set(re.findall(r'function ([a-zA-Z0-9_]+)\(', full_text))
print(f"JS functions count: {len(func_defs)}")

# 4. Check CSS background-clip
bg_clips = re.findall(r'background-clip\s*:\s*text', full_text)
webkit_bg_clips = re.findall(r'-webkit-background-clip\s*:\s*text', full_text)
print(f"CSS background-clip count: standard={len(bg_clips)}, webkit={len(webkit_bg_clips)}")

# 5. Check event listeners
listeners = re.findall(r'addEventListener\(["\']([^"\']+)["\']', full_text)
print("Event listeners:", set(listeners))
