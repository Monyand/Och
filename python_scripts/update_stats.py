import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # Update ROP stats
        old_rop_stats = """<span class="text-xs font-medium text-slate-500 dark:text-slate-400 hidden sm:inline-block px-2 py-1 bg-slate-200 dark:bg-slate-800 rounded-md">
                                ${ropVopCount} ВОП, ${ropItemCount} поз.
                            </span>"""
        
        new_rop_stats = """<div class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-200/80 dark:bg-slate-700/80 rounded-md text-[11px] font-medium text-slate-500 dark:text-slate-400 border border-slate-300 dark:border-slate-600">
                                <span><strong class="text-sm text-indigo-600 dark:text-indigo-400">${ropVopCount}</strong> ВОП</span>
                                <span class="w-1 h-1 rounded-full bg-slate-400 dark:bg-slate-500"></span>
                                <span><strong class="text-sm text-amber-600 dark:text-amber-400">${ropItemCount}</strong> поз.</span>
                            </div>"""

        # Update VOP stats
        old_vop_stats = """<span class="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-1 rounded-md shrink-0">
                                        ${childCount} БП
                                    </span>"""
        
        new_vop_stats = """<span class="flex items-center gap-1 text-[11px] font-medium text-slate-500 dark:text-slate-400 bg-slate-200/80 dark:bg-slate-700/80 px-2 py-1 rounded-md shrink-0 border border-slate-300 dark:border-slate-600">
                                        <strong class="text-[13px] text-teal-600 dark:text-teal-400">${childCount}</strong> БП
                                    </span>"""

        if old_rop_stats in text:
            text = text.replace(old_rop_stats, new_rop_stats)
        else:
            print("Warning: old_rop_stats not found exactly as string. Will try regex.")
            # If spacing doesn't match perfectly
            text = re.sub(
                r'<span class="text-xs font-medium text-slate-500 dark:text-slate-400 hidden sm:inline-block px-2 py-1 bg-slate-200 dark:bg-slate-800 rounded-md">\s*\$\{ropVopCount\} ВОП, \$\{ropItemCount\} поз\.\s*</span>',
                new_rop_stats, text
            )

        if old_vop_stats in text:
            text = text.replace(old_vop_stats, new_vop_stats)
        else:
            print("Warning: old_vop_stats not found exactly as string. Will try regex.")
            text = re.sub(
                r'<span class="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-1 rounded-md shrink-0">\s*\$\{childCount\} БП\s*</span>',
                new_vop_stats, text
            )

        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully updated the stats badges!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
