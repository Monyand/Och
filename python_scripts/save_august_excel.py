import zipfile
import shutil
import os
import tempfile

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'
out_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика_ОНОВЛЕНО.xlsx'

temp_dir = tempfile.mkdtemp()
try:
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    sheet_path = os.path.join(temp_dir, 'xl', 'worksheets', 'sheet1.xml')
    if os.path.exists(sheet_path):
        with open(sheet_path, 'r', encoding='utf-8') as f:
            sheet_content = f.read()

        col_names = ["D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH"]
        
        for day in range(1, 32):
            col = col_names[day - 1]
            date_str = f"{day:02d}.08.2026"
            
            old_cell_start = f'<c r="{col}1" s="2">'
            if old_cell_start in sheet_content:
                idx = sheet_content.find(old_cell_start)
                end_idx = sheet_content.find('</c>', idx)
                if idx != -1 and end_idx != -1:
                    new_cell = f'<c r="{col}1" s="2" t="inlineStr"><is><t>{date_str}</t></is></c>'
                    sheet_content = sheet_content[:idx] + new_cell + sheet_content[end_idx+4:]

        with open(sheet_path, 'w', encoding='utf-8') as f:
            f.write(sheet_content)

    # Save to out_path
    if os.path.exists(out_path):
        os.remove(out_path)
        
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, temp_dir)
                z_out.write(full_p, rel_p)

    print(f"SUCCESS: Created updated file {out_path}")

    # Try replacing original if not locked
    try:
        shutil.copy2(out_path, file_path)
        print("Also updated original file directly!")
    except Exception as e:
        print("Original file is currently open in Excel, so updated version saved as _ОНОВЛЕНО.xlsx")

finally:
    shutil.rmtree(temp_dir)
