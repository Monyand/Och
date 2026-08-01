import zipfile
import xml.etree.ElementTree as ET

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

with zipfile.ZipFile(file_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('xl/worksheets/') or name == 'xl/sharedStrings.xml':
            print(f"=== {name} ===")
            content = z.read(name).decode('utf-8', errors='replace')
            print(content[:2000])
