import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            lines = f.readlines()
            
        # We need to find line 1227. It should contain '}500 hover:text-red-700'
        # Let's search for this exact string to be safe.
        
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if '}500 hover:text-red-700' in line:
                start_idx = i
                break
                
        if start_idx != -1:
            # Find the end of the duplicated block. We know it ends with:
            # statsBadge.innerText = `📊 Всього: ${totalRops} РОПів, ${totalVops} ВОПів, ${totalItems} позицій`;
            # }
            # }
            # Then followed by function escapeHtml
            
            for i in range(start_idx, len(lines)):
                if 'function escapeHtml(str)' in lines[i]:
                    # Go back to the '}' that closes the duplicate
                    for j in range(i-1, start_idx, -1):
                        if lines[j].strip() == '}':
                            end_idx = j
                            break
                    break
                    
            if end_idx != -1:
                # Fix start_idx line to just contain '        }'
                lines[start_idx] = '        }\n'
                
                # Delete lines from start_idx + 1 to end_idx
                del lines[start_idx+1 : end_idx+1]
                
                with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
                    f.writelines(lines)
                print(f"Successfully deleted junk lines from {start_idx+1} to {end_idx+1}")
            else:
                print("Could not find the end of the junk block.")
        else:
            print("Could not find the start of the junk block.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
