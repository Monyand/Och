import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        new_func = """function addRopItem(rIdx, type) {
            if (!currentRopData[rIdx]) return;
            if (!currentRopData[rIdx].items) currentRopData[rIdx].items = [];

            if (type === 'subRop') {
                currentRopData[rIdx].items.push({
                    type: 'subRop',
                    name: `ВОП "${currentRopData[rIdx].items.length + 1}"`,
                    children: [
                        { type: 'direct', name: 'БП 1' }
                    ]
                });
            } else {
                let items = currentRopData[rIdx].items;
                let lastDirectIdx = -1;
                for (let i = items.length - 1; i >= 0; i--) {
                    if (items[i].type === 'direct') {
                        lastDirectIdx = i;
                        break;
                    }
                }
                const newItem = {
                    type: 'direct',
                    name: `КСП "${items.length + 1}"`
                };
                if (lastDirectIdx !== -1) {
                    items.splice(lastDirectIdx + 1, 0, newItem);
                } else {
                    items.unshift(newItem);
                }
            }
            syncTextFromRop();
            renderVisualRopHierarchy();
        }"""

        # Match function addRopItem until the closing brace before function updateItemName
        pattern = r'function addRopItem\(rIdx, type\) \{.*?syncTextFromRop\(\);\s*renderVisualRopHierarchy\(\);\s*\}'
        
        if re.search(pattern, text, flags=re.DOTALL):
            text = re.sub(pattern, new_func, text, flags=re.DOTALL)
            with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(text)
            print("Successfully implemented smart direct item grouping logic!")
        else:
            print("Could not match the addRopItem function.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
