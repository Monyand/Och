import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        handle = '<span class="cursor-grab text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-1 font-bold text-lg leading-none" title="Потягніть, щоб перемістити">⋮⋮</span>'
        
        # Inject handle into direct item
        text = text.replace(
            '<span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-amber-500 text-white shrink-0 shadow-sm">\n                                    Пряма позиція\n                                </span>',
            handle + '\n                                <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-amber-500 text-white shrink-0 shadow-sm">\n                                    Пряма позиція\n                                </span>'
        )
        
        # Inject handle into subRop item
        text = text.replace(
            '<span class="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded bg-indigo-600 text-white shadow-sm shrink-0">\n                                        ВОП / ГРУПА\n                                    </span>',
            handle + '\n                                    <span class="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded bg-indigo-600 text-white shadow-sm shrink-0">\n                                        ВОП / ГРУПА\n                                    </span>'
        )
        
        # Inject handle into child item
        text = text.replace(
            '<span class="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0"></span>',
            handle + '\n                                            <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0"></span>'
        )
        
        # Inject handle into Main Rop card header
        text = text.replace(
            '<span class="px-2.5 py-1 text-xs font-black uppercase rounded-lg bg-blue-600 text-white shrink-0 shadow-sm">\n                                РОП\n                            </span>',
            handle + '\n                            <span class="px-2.5 py-1 text-xs font-black uppercase rounded-lg bg-blue-600 text-white shrink-0 shadow-sm">\n                                РОП\n                            </span>'
        )

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully added drag handles!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
