import re
import sys

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # Fix 1: collapsedRops -> collapsedRopIndices in the newly added functions
        text = text.replace('let collapsedRops = new Set();', 'let collapsedRopIndices = new Set();')
        text = text.replace('collapsedRops.has', 'collapsedRopIndices.has')
        text = text.replace('collapsedRops.delete', 'collapsedRopIndices.delete')
        text = text.replace('collapsedRops.add', 'collapsedRopIndices.add')
        text = text.replace('collapsedRops.clear', 'collapsedRopIndices.clear')
        
        # Fix 2: Repair the corrupted line 1059
        # The corrupted text is something like:
        # const isExplicitVop = trimmed.toLowerCase().startsWith('        function renderVisualRopHierarchy() {
        
        # We need to find the exact corrupted string. We'll use regex to match the end of parseRopHierarchy.
        # It looks like:
        # } else {
        #     const isExplicitVop = trimmed.toLowerCase().startsWith('<something corrupted>        function renderVisualRopHierarchy() {
        
        # Let's search for "const isExplicitVop = trimmed.toLowerCase().startsWith(" and replace until "function renderVisualRopHierarchy() {"
        
        pattern = r"const isExplicitVop = trimmed\.toLowerCase\(\)\.startsWith\([^f]*function renderVisualRopHierarchy\(\) \{"
        
        repaired_code = """const isExplicitVop = trimmed.toLowerCase().startsWith('воп') || trimmed.toLowerCase().startsWith('vop');
                    if (isExplicitVop) {
                        currentSubRop = { type: 'subRop', name: trimmed, children: [] };
                        if (currentMainRop) currentMainRop.items.push(currentSubRop);
                    } else {
                        if (currentMainRop) currentMainRop.items.push({ type: 'direct', name: trimmed });
                    }
                }
            });
            return ropList;
        }

        function renderVisualRopHierarchy() {"""
        
        text = re.sub(pattern, repaired_code, text)
        
        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully repaired the syntax error and fixed collapsedRopIndices!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
