import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        new_func = """const buildBreakdownText = (unitMap, nameHint = '') => {
                const lines = [];
                let total = 0;

                for (let [unit, cnt] of Object.entries(unitMap)) {
                    if (cnt > 0) {
                        lines.push(`${unit} - ${cnt} в/сл`);
                        total += cnt;
                    }
                }
                return { text: lines.join('\\n'), total };
            };"""

        # Replace the function
        pattern = r'const buildBreakdownText = \(unitMap, nameHint = \'\'\) => \{.*?return \{ text: isNoBreakdown \? "" : lines\.join\(\'\\n\'\), total \};\s*\}'
        
        if re.search(pattern, text, flags=re.DOTALL):
            text = re.sub(pattern, new_func, text, flags=re.DOTALL)
            with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(text)
            print("Successfully removed isNoBreakdown logic!")
        else:
            print("Could not find buildBreakdownText to replace.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
