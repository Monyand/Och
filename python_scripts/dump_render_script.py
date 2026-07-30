import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        match = re.search(r'function renderVisualRopHierarchy\(\) \{.*?(?=function \w+\()', text, re.DOTALL)
        if match:
            with open('dump_render.js', 'w', encoding='utf-8') as f:
                f.write(match.group(0))
            print("Successfully dumped renderVisualRopHierarchy to dump_render.js")
        else:
            print("Function not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
