import re
import sys

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
            
        scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
        
        # We assume the main script is the largest one
        main_script = max(scripts, key=len)
        
        with open('test_syntax.js', 'w', encoding='utf-8') as f:
            f.write(main_script)
            
        print("Script extracted to test_syntax.js")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
