import zipfile

file_path = r'd:\ОЧ\Програми\УСІ_ПЕРЕВІРКИ_01.08_логістика.xlsx'

with zipfile.ZipFile(file_path, 'r') as z:
    if 'xl/styles.xml' in z.namelist():
        print(z.read('xl/styles.xml').decode('utf-8', errors='replace'))
