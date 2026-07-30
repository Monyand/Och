import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # The current bottom buttons block:
        bottom_buttons = """<div class="pt-4 mt-2 flex gap-3 border-t border-slate-200 dark:border-slate-700">
                            <button type="button" onclick="addRopItem(${rIdx}, 'direct')"
                                class="text-xs bg-amber-500 hover:bg-amber-600 text-white font-medium py-2 px-4 rounded-md transition-colors shadow-sm">
                                + Пряма позиція (КСП/БП)
                            </button>
                            <button type="button" onclick="addRopItem(${rIdx}, 'subRop')"
                                class="text-xs bg-indigo-500 hover:bg-indigo-600 text-white font-medium py-2 px-4 rounded-md transition-colors shadow-sm">
                                + ВОП (Група)
                            </button>
                        </div>"""

        # Remove it from the bottom
        text = text.replace(bottom_buttons, "")

        # Inject it at the top of the body
        top_injection = f"""<div id="rop-card-body-${{rIdx}}" class="${{isCollapsed ? 'hidden ' : ''}}p-5">
                        {bottom_buttons.replace('pt-4 mt-2 border-t', 'pb-4 mb-4 border-b').replace('pt-4 mt-2', 'pb-4 mb-4 border-b')}
                        <div class="space-y-1">"""

        text = text.replace(
            '<div id="rop-card-body-${rIdx}" class="${isCollapsed ? \'hidden \' : \'\'}p-5">\n                        <div class="space-y-1">',
            top_injection
        )

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully moved the buttons to the top!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
