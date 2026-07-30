import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        def repl(match):
            func_body = match.group(0)
            func_body = func_body.replace('items.unshift(', 'items.push(')
            return func_body

        # Match function addRopItem block until syncTextFromRop()
        text = re.sub(r'function addRopItem\(rIdx, type\) \{.*?syncTextFromRop\(\);\s*\}', repl, text, flags=re.DOTALL)

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully reverted addRopItem back to push!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
