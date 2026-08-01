import zipfile
import xml.etree.ElementTree as ET

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

with zipfile.ZipFile(file_path, 'r') as z:
    for name in z.namelist():
        content = z.read(name).decode('utf-8', errors='replace')
        if '07' in content or 'лип' in content.lower():
            print(f"FOUND '07' or 'липень' IN FILE: {name}")
            # Print lines containing 07
            for line in content.split('>'):
                if '07' in line or 'лип' in line.lower():
                    print("  LINE:", line[:150])
