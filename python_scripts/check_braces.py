def check_balance(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
        
    import re
    # Extract only the content inside <script> tags
    scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
    if not scripts:
        print("No script tags found.")
        return
        
    main_script = max(scripts, key=len)
    
    # Remove comments and strings to avoid false positives
    code = re.sub(r'//.*', '', main_script)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'(["\'`])(?:(?=(\\?))\2.)*?\1', '', code, flags=re.DOTALL)
    
    stack = []
    pairs = {'}': '{', ')': '(', ']': '['}
    
    lines = code.split('\n')
    for line_num, line in enumerate(lines):
        for char in line:
            if char in '{[(':
                stack.append((char, line_num + 1))
            elif char in '}])':
                if not stack:
                    print(f"Unmatched closing {char} on line {line_num + 1}")
                    return
                top, _ = stack.pop()
                if top != pairs[char]:
                    print(f"Mismatched closing {char} on line {line_num + 1}")
                    return
                    
    if stack:
        print(f"Unmatched opening brackets remaining: {stack}")
    else:
        print("All brackets are balanced perfectly!")

check_balance('Додаток 6 test.html')
