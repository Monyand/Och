import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # Find the addRopItem function and replace push with unshift
        # It looks something like:
        # function addRopItem(rIdx, type) {
        #     if (!currentRopData[rIdx]) return;
        #     if (!currentRopData[rIdx].items) currentRopData[rIdx].items = [];
        #
        #     if (type === 'subRop') {
        #         currentRopData[rIdx].items.push({
        
        # We can just replace currentRopData[rIdx].items.push with currentRopData[rIdx].items.unshift inside this function.
        # But we must be careful not to break other pushes if any. Actually, addRopItem only has two pushes for items.
        
        # Let's extract the whole function using a better regex, or just replace all instances in a specific block.
        
        def repl(match):
            func_body = match.group(0)
            func_body = func_body.replace('items.push(', 'items.unshift(')
            return func_body

        # Match function addRopItem block until syncTextFromRop()
        text = re.sub(r'function addRopItem\(rIdx, type\) \{.*?syncTextFromRop\(\);\s*\}', repl, text, flags=re.DOTALL)

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully updated addRopItem to use unshift!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
