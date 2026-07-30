import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # 1. Read the original renderVisualRopHierarchy from dump_render.js
        with open('dump_render.js', 'r', encoding='utf-8') as f:
            original_render_func = f.read()

        # Replace the current renderVisualRopHierarchy with the original one
        # Find the current one in text:
        match = re.search(r'function renderVisualRopHierarchy\(\) \{.*?(?=function \w+\()', text, re.DOTALL)
        if match:
            text = text.replace(match.group(0), original_render_func)
            print("Successfully reverted renderVisualRopHierarchy")
        else:
            print("Could not find renderVisualRopHierarchy in test.html")

        # 2. Remove the injected JS functions
        dd_js_pattern = r'let draggedItem = null;.*?document\.addEventListener\(\'dragend\', \(\w+\) => \{[^\}]+\}\);'
        text = re.sub(dd_js_pattern, '', text, flags=re.DOTALL)
        
        # Clean up any remaining whitespace above escapeHtml
        text = re.sub(r'\s+function escapeHtml\(str\) \{', '\n\n        function escapeHtml(str) {', text)

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully removed Drag & Drop feature!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
