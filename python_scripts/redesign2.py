import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        new_func = """function renderVisualRopHierarchy() {
            const container = document.getElementById('rop-cards-container');
            const statsBadge = document.getElementById('rop-stats-badge');
            if (!container) return;

            container.innerHTML = '';

            let totalRops = currentRopData.length;
            let totalVops = 0;
            let totalItems = 0;

            currentRopData.forEach((mainRop, rIdx) => {
                const card = document.createElement('div');
                card.className = "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm overflow-hidden mb-5";

                const isCollapsed = collapsedRopIndices.has(rIdx);

                let ropVopCount = 0;
                let ropItemCount = 0;
                let itemsHtml = '';

                mainRop.items.forEach((item, iIdx) => {
                    if (item.type === 'subRop') {
                        totalVops++;
                        ropVopCount++;
                        let childCount = item.children ? item.children.length : 0;
                        totalItems += childCount;
                        ropItemCount += childCount;

                        let childrenHtml = '';
                        if (item.children) {
                            item.children.forEach((child, cIdx) => {
                                childrenHtml += `
                                    <div class="flex items-center gap-2 group">
                                        <div class="w-1.5 h-1.5 rounded-full bg-indigo-400 dark:bg-indigo-500 shrink-0"></div>
                                        <input type="text" value="${escapeHtml(child.name)}" 
                                            onchange="updateChildItemName(${rIdx}, ${iIdx}, ${cIdx}, this.value)"
                                            class="flex-1 px-2.5 py-1 text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-md text-slate-800 dark:text-slate-100 placeholder-slate-400"
                                            placeholder='БП / СП (напр., "БП Дакота")'>
                                        <button type="button" onclick="deleteChildItem(${rIdx}, ${iIdx}, ${cIdx})"
                                            class="text-slate-400 hover:text-red-500 p-1 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20" title="Видалити БП">
                                            ✕
                                        </button>
                                    </div>
                                `;
                            });
                        }

                        itemsHtml += `
                            <div class="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 border-l-4 border-l-indigo-500 rounded-lg p-3 my-3 shadow-sm">
                                <div class="flex items-center gap-2 mb-3">
                                    <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-indigo-500 text-white shrink-0">
                                        ВОП / ГРУПА
                                    </span>
                                    <input type="text" value="${escapeHtml(item.name)}" 
                                        onchange="updateItemName(${rIdx}, ${iIdx}, this.value)"
                                        class="flex-1 px-3 py-1.5 text-sm font-semibold bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-md text-slate-800 dark:text-slate-100 placeholder-slate-400"
                                        placeholder='Назва ВОПа (напр., "ВОП Атлантик")'>
                                    <span class="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-1 rounded-md shrink-0">
                                        ${childCount} БП
                                    </span>
                                    <button type="button" onclick="convertToDirectItem(${rIdx}, ${iIdx})"
                                        class="text-xs text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md transition-colors"
                                        title="Зробити самостійною позицією без вкладених БП">
                                        ↳ Пряма
                                    </button>
                                    <button type="button" onclick="deleteRopItem(${rIdx}, ${iIdx})"
                                        class="text-slate-400 hover:text-red-500 p-1.5 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20" title="Видалити ВОП">
                                        ✕
                                    </button>
                                </div>

                                <div class="ml-2 pl-3 border-l-2 border-indigo-200 dark:border-indigo-800/50 space-y-2">
                                    ${childrenHtml || '<p class="text-xs text-slate-400 italic py-1">Немає вкладених БП</p>'}
                                    <div class="pt-1">
                                        <button type="button" onclick="addSubItem(${rIdx}, ${iIdx})"
                                            class="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold px-2 py-1 rounded-md hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors">
                                            + Додати підпорядкований БП / СП
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        totalItems++;
                        ropItemCount++;
                        itemsHtml += `
                            <div class="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 border-l-4 border-l-amber-500 rounded-lg p-3 my-3 shadow-sm flex items-center gap-2">
                                <span class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-amber-500 text-white shrink-0">
                                    Пряма позиція
                                </span>
                                <input type="text" value="${escapeHtml(item.name)}" 
                                    onchange="updateItemName(${rIdx}, ${iIdx}, this.value)"
                                    class="flex-1 px-3 py-1.5 text-sm font-semibold bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 rounded-md text-slate-800 dark:text-slate-100 placeholder-slate-400"
                                    placeholder='КСП / БП / ВОП ("КСП Невада")'>
                                <button type="button" onclick="convertToSubRopItem(${rIdx}, ${iIdx})"
                                    class="text-xs text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md transition-colors"
                                    title="Додати можливість вкладати в нього БП">
                                    + Перетворити на ВОП
                                </button>
                                <button type="button" onclick="deleteRopItem(${rIdx}, ${iIdx})"
                                    class="text-slate-400 hover:text-red-500 p-1.5 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20" title="Видалити">
                                    ✕
                                </button>
                            </div>
                        `;
                    }
                });

                card.innerHTML = `
                    <div class="px-4 py-3 bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between gap-3">
                        <div class="flex items-center gap-3 flex-1">
                            <button type="button" onclick="toggleRopCard(${rIdx})" 
                                class="text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 p-1 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors w-7 h-7 flex items-center justify-center" title="Згорнути / Розгорнути РОП">
                                <span id="rop-card-icon-${rIdx}" class="text-[10px] font-bold">${isCollapsed ? '▼' : '▲'}</span>
                            </button>
                            <span class="px-3 py-1 text-xs font-black uppercase rounded bg-blue-600 text-white shrink-0 shadow-sm">
                                РОП
                            </span>
                            <input type="text" value="${escapeHtml(mainRop.ropName)}"
                                onchange="updateMainRopName(${rIdx}, this.value)"
                                class="flex-1 px-3 py-1.5 text-sm font-bold bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-slate-400"
                                placeholder='Назва РОПа (напр., "РОП 5 мр 2 мб")'>
                            <span class="text-xs font-medium text-slate-500 dark:text-slate-400 hidden sm:inline-block px-2 py-1 bg-slate-200 dark:bg-slate-800 rounded-md">
                                ${ropVopCount} ВОП, ${ropItemCount} поз.
                            </span>
                        </div>
                        <button type="button" onclick="deleteMainRopNode(${rIdx})"
                            class="text-red-600 dark:text-red-400 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-md text-xs font-semibold transition-colors flex items-center gap-1 border border-red-200 dark:border-red-800/50"
                            title="Видалити весь РОП">
                            <span>Видалити РОП</span>
                        </button>
                    </div>

                    <div id="rop-card-body-${rIdx}" class="${isCollapsed ? 'hidden ' : ''}p-5">
                        <div class="space-y-1">
                            ${itemsHtml || '<div class="text-sm text-slate-400 italic text-center py-6">Немає доданих позицій або ВОПів. Додайте їх кнопками нижче.</div>'}
                        </div>

                        <div class="pt-4 mt-2 flex gap-3 border-t border-slate-200 dark:border-slate-700">
                            <button type="button" onclick="addRopItem(${rIdx}, 'direct')"
                                class="text-xs bg-amber-500 hover:bg-amber-600 text-white font-medium py-2 px-4 rounded-md transition-colors shadow-sm">
                                + Пряма позиція (КСП/БП)
                            </button>
                            <button type="button" onclick="addRopItem(${rIdx}, 'subRop')"
                                class="text-xs bg-indigo-500 hover:bg-indigo-600 text-white font-medium py-2 px-4 rounded-md transition-colors shadow-sm">
                                + ВОП (Група)
                            </button>
                        </div>
                    </div>
                `;

                container.appendChild(card);
            });

            if (statsBadge) {
                statsBadge.innerText = `📊 Всього: ${totalRops} РОПів, ${totalVops} ВОПів, ${totalItems} позицій`;
            }
        }"""
        
        match = re.search(r'function renderVisualRopHierarchy\(\) \{.*?(?=function \w+\()', text, re.DOTALL)
        if match:
            text = text.replace(match.group(0), new_func + '\n\n        ')
            
        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully applied the highly readable UI redesign!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
