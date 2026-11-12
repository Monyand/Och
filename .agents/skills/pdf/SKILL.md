---
name: PDF Processing
description: Робота з PDF-файлами у Windows: витягування тексту й таблиць (pdfplumber, pypdf), об'єднання/розбиття документів, OCR сканів та генерація PDF із підтримкою української кирилиці (ReportLab). Активувати при будь-якому згадуванні .pdf файлів.
---

# Обробка та генерація PDF (Windows + Python)

## 1. Доступні інструменти та бібліотеки
Перед запуском скриптів перевір наявність потрібних пакетів у Python (`pypdf`, `pdfplumber`, `reportlab`, `pytesseract`, `pdf2image`). Якщо чогось не вистачає — встанови точково (`pip install pypdf pdfplumber` тощо) або попередь користувача.

| Задача | Інструмент | Примітка для Windows |
|---|---|---|
| Читання тексту, метаданих, зшивання/розбиття, поворот, шифрування | `pypdf` | Нативно в Python, без зовнішніх утиліт |
| Витяг структурованих таблиць (списки о/с, табелі, накази) | `pdfplumber` | Найкраще перетворює табличні PDF у `DataFrame` / `openpyxl` |
| Генерація PDF-звітів | `reportlab` | **Обов'язково реєструвати TTF шрифт для кирилиці!** |
| OCR зі сканів PDF | `pytesseract` + `pdf2image` | Потребує встановлених у системі Tesseract OCR (`ukr`+`eng`) та Poppler |

---

## 2. Критичні правила для кирилиці та Windows

### Кирилиця в ReportLab (Обов'язково!)
Стандартні вбудовані шрифти ReportLab (`Helvetica`, `Times-Roman`, `Courier`) **НЕ підтримують українську кирилицю** (рендерять чорні квадратики або сміття) і не містять Unicode під-/надрядкових індексів (`₀₁₂`, `⁰¹²`).
Завжди підключай системний TrueType-шрифт із підтримкою кирилиці:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Calibri', r'C:\Windows\Fonts\calibri.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', r'C:\Windows\Fonts\calibrib.ttf'))
# Або Arial: C:\Windows\Fonts\arial.ttf / arialbd.ttf
```
- Для індексів у `Paragraph` використовуй XML-теги `<sub>...</sub>` та `<super>...</super>`, а не Unicode-символи індексів.

---

## 3. Типові рецепти (`pypdf` та `pdfplumber`)

### Витягти текст (базово)
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
for i, page in enumerate(reader.pages, start=1):
    print(f"--- Сторінка {i} ---")
    print(page.extract_text() or "")
```

### Витягти таблиці з PDF напряму в Excel (`pdfplumber` + `openpyxl`)
```python
import pdfplumber
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Витяг з PDF"

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        for table in page.extract_tables() or []:
            for row in table:
                ws.append([cell.replace("\n", " ").strip() if cell else "" for cell in row])

wb.save("extracted_tables.xlsx")
```
> Порада: якщо таблиця без чітких рамок (`borderless`), передай `page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})`.

### Зшити або розділити PDF (`pypdf`)
```python
from pypdf import PdfWriter, PdfReader

# Зшити кілька PDF
writer = PdfWriter()
for path in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(path).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)
```

### Розділити по сторінках / вибрати діапазон / повернути
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages[0:5]:  # перші 5 сторінок
    writer.add_page(page)
# Поворот за годинниковою стрілкою: page.rotate(90)
with open("subset.pdf", "wb") as f:
    writer.write(f)
```

### Створити багатосторінковий PDF з таблицями (`reportlab.platypus`)
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("ArialUA", r"C:\Windows\Fonts\arial.ttf"))
style = ParagraphStyle("BodyUA", fontName="ArialUA", fontSize=10, leading=14)

doc = SimpleDocTemplate("report.pdf", pagesize=A4)
story = [Paragraph("Зведений звіт", style), Spacer(1, 12)]
doc.build(story)
```

---

## 4. Скановані PDF (OCR)
Якщо `page.extract_text()` повертає порожній рядок — перед нами растровий скан.
1. Конвертувати сторінки через `pdf2image.convert_from_path(...)` (або рендер через `pypdfium2` / `fitz`, якщо немає Poppler).
2. Розпізнавати через `pytesseract.image_to_string(img, lang="ukr+eng")`.
3. Перед збереженням у таблицю обов'язково пропускати розпізнаний текст через нормалізацію омогліфів і дат згідно з [Tactical Parsing Standards](file:///d:/ОЧ/Програми/.agents/skills/tactical_parsing_standards/SKILL.md).

