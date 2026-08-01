import os
import glob

docx_files = glob.glob(r'd:\ОЧ\Програми\*.docx') + glob.glob(r'd:\ОЧ\Програми\**\*.docx', recursive=True)
xlsx_files = glob.glob(r'd:\ОЧ\Програми\*.xlsx') + glob.glob(r'd:\ОЧ\Програми\**\*.xlsx', recursive=True)

print("DOCX files found:", docx_files)
print("XLSX files found:", xlsx_files)
