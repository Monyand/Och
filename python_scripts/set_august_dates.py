import zipfile
import shutil
import os
import tempfile
import xml.etree.ElementTree as ET

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

temp_dir = tempfile.mkdtemp()
try:
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 1. Update styles.xml to add custom number format dd.mm.yyyy
    styles_path = os.path.join(temp_dir, 'xl', 'styles.xml')
    if os.path.exists(styles_path):
        with open(styles_path, 'r', encoding='utf-8') as f:
            styles_content = f.read()

        # Insert numFmts if missing or update numFmtId
        if '<numFmts' not in styles_content:
            numfmt_xml = '<numFmts count="1"><numFmt numFmtId="165" formatCode="dd.mm.yyyy"/></numFmts>'
            styles_content = styles_content.replace('<styleSheet ', '<styleSheet ' + '').replace('><fonts ', '>' + numfmt_xml + '<fonts ')
        
        # Change cellXfs index 2 numFmtId to 165
        styles_content = styles_content.replace('numFmtId="14" fontId="2"', 'numFmtId="165" fontId="2"')

        with open(styles_path, 'w', encoding='utf-8') as f:
            f.write(styles_content)

    # 2. Update sheet1.xml to ensure dates 46204 to 46234 (August 2026)
    sheet_path = os.path.join(temp_dir, 'xl', 'worksheets', 'sheet1.xml')
    if os.path.exists(sheet_path):
        with open(sheet_path, 'r', encoding='utf-8') as f:
            sheet_content = f.read()

        # Map D1:AH1 to serial numbers 46204..46234
        start_date = 46204 # 01.08.2026
        for day in range(1, 32):
            col_names = ["D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH"]
            col = col_names[day - 1]
            val = start_date + (day - 1)
            # Replace value for cell
            pattern_old = f'<c r="{col}1" s="2"><v>'
            if pattern_old in sheet_content:
                # Find end of v tag
                idx = sheet_content.find(pattern_old)
                end_idx = sheet_content.find('</v></c>', idx)
                if idx != -1 and end_idx != -1:
                    sheet_content = sheet_content[:idx] + f'<c r="{col}1" s="2"><v>{val}</v></c>' + sheet_content[end_idx+8:]

        with open(sheet_path, 'w', encoding='utf-8') as f:
            f.write(sheet_content)

    # Pack back into zip
    zip_out = file_path + '.tmp'
    with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, temp_dir)
                z_out.write(full_p, rel_p)

    shutil.move(zip_out, file_path)
    print("SUCCESS: Updated Excel dates to August 08.2026 (01.08.2026 - 31.08.2026) with explicit format dd.mm.yyyy!")

finally:
    shutil.rmtree(temp_dir)
