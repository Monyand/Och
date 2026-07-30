import re
import sys

def main():
    try:
        # We use surrogateescape to preserve invalid bytes like 0xd0
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        code_to_insert = """
        let collapsedRops = new Set();

        function syncTextFromRop() {
            let textLines = [];
            currentRopData.forEach(rop => {
                textLines.push(`[${rop.ropName}]`);
                if (rop.items) {
                    rop.items.forEach(item => {
                        if (item.type === 'direct') {
                            textLines.push(item.name);
                        } else if (item.type === 'subRop') {
                            if (item.children && item.children.length > 0) {
                                textLines.push(item.name);
                                item.children.forEach(child => {
                                    textLines.push(`- ${child.name}`);
                                });
                            } else {
                                textLines.push(`[[${item.name}]]`);
                            }
                        }
                    });
                }
                textLines.push('');
            });
            
            const ta = document.getElementById('kw-rop-hierarchy');
            if(ta) ta.value = textLines.join('\\n').trim();
        }

        function syncRopFromText() {
            const ta = document.getElementById('kw-rop-hierarchy');
            if(ta) {
                currentRopData = parseRopHierarchy(ta.value);
                renderVisualRopHierarchy();
            }
        }

        function toggleRopCard(rIdx) {
            if (collapsedRops.has(rIdx)) {
                collapsedRops.delete(rIdx);
            } else {
                collapsedRops.add(rIdx);
            }
            renderVisualRopHierarchy();
        }

        function collapseAllRops() {
            currentRopData.forEach((_, idx) => collapsedRops.add(idx));
            renderVisualRopHierarchy();
        }

        function expandAllRops() {
            collapsedRops.clear();
            renderVisualRopHierarchy();
        }
        """

        # Insert after "let currentRopData = [];"
        if 'let currentRopData = [];' in text:
            new_text = text.replace('let currentRopData = [];', 'let currentRopData = [];\n' + code_to_insert, 1)
            
            with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(new_text)
                
            print("Successfully inserted missing functions!")
        else:
            print("Could not find 'let currentRopData = [];' to anchor the insertion.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
