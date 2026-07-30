import re
import sys

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        start = -1
        end = -1
        
        for i, line in enumerate(lines):
            if '4. Ієрархія РОПів та ВОПів' in line:
                start = i
                break
                
        if start != -1:
            div_count = 0
            started = False
            for i in range(start - 5, len(lines)):
                line = lines[i]
                if '<div' in line:
                    div_count += line.count('<div')
                    started = True
                if '</div' in line:
                    div_count -= line.count('</div')
                if started and div_count <= 0:
                    end = i
                    break
            
            print("".join(lines[max(0, start-5):min(len(lines), end+1)]))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
