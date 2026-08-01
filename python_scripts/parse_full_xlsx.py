import zipfile
import xml.etree.ElementTree as ET

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

with zipfile.ZipFile(file_path, 'r') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for elem in tree.iter():
            if elem.tag.endswith('t'):
                shared_strings.append(elem.text or '')

    print(f"--- SHARED STRINGS ({len(shared_strings)}) ---")
    for idx, s in enumerate(shared_strings):
        print(f"[{idx}]: {s}")

    sheet_xml = z.read('xl/worksheets/sheet1.xml')
    tree = ET.fromstring(sheet_xml)
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    print("\n--- CELL VALUES ---")
    for row in tree.findall('.//s:row', ns):
        r_num = row.attrib.get('r')
        row_str = []
        for cell in row.findall('s:c', ns):
            c_ref = cell.attrib.get('r')
            c_type = cell.attrib.get('t')
            val_elem = cell.find('s:v', ns)
            val = val_elem.text if val_elem is not None else ''
            if c_type == 's' and val.isdigit():
                val = shared_strings[int(val)]
            row_str.append(f"{c_ref}: '{val}'")
        if row_str:
            print(f"Row {r_num}: {', '.join(row_str)}")
