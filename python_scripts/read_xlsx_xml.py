import zipfile
import xml.etree.ElementTree as ET

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

with zipfile.ZipFile(file_path, 'r') as z:
    # Shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for elem in tree.iter():
            if elem.tag.endswith('t'):
                shared_strings.append(elem.text or '')
    
    print(f"Total shared strings: {len(shared_strings)}")
    print("Sample strings:")
    for s in shared_strings[:30]:
        print("  -", s)

    # List sheet files
    sheets = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet')]
    print("Sheet files:", sheets)
