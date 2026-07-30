import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # Fix the substring matching bug in buildBreakdownText
        old_str = "const isNoBreakdown = hintLower.includes('заб') || hintLower.includes('бро');"
        new_str = "const isNoBreakdown = hintLower.includes('забезпеч') || hintLower.includes('бронегр');"
        
        if old_str in text:
            text = text.replace(old_str, new_str)
            with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(text)
            print("Successfully fixed the 'Діброва' bug!")
        else:
            print("Could not find the exact string to replace. Trying regex...")
            # Fallback regex
            text, count = re.subn(r"const isNoBreakdown = hintLower\.includes\('заб'\) \|\| hintLower\.includes\('бро'\);", new_str, text)
            if count > 0:
                with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                    f.write(text)
                print("Successfully fixed via regex!")
            else:
                print("Failed completely.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
