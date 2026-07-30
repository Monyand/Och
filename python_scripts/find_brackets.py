import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        match = re.search(r'<script>(.*?)</script>', text, re.DOTALL)
        if match:
            script = match.group(1)
            lines = script.split('\n')
            stack = []
            
            # A very simple heuristic string removal before counting brackets
            # This handles single quotes, double quotes and template literals
            script_no_strings = re.sub(r'(".*?"|\'.*?\'|`.*?`)', '""', script, flags=re.DOTALL)
            script_no_comments = re.sub(r'//.*?\n', '\n', script_no_strings)
            script_clean = re.sub(r'/\*.*?\*/', '', script_no_comments, flags=re.DOTALL)
            
            # Now just count brackets
            balance = 0
            for i, char in enumerate(script_clean):
                if char == '{':
                    balance += 1
                elif char == '}':
                    balance -= 1
                    if balance < 0:
                        print("Too many closing brackets!")
                        break
            
            print(f"Final balance (should be 0): {balance}")
            
            # If balance > 0, we have an unclosed {
            if balance > 0:
                print("We have an unclosed {.")
        else:
            print("No script tag found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
