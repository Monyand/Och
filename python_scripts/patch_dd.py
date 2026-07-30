import re

def main():
    try:
        with open('Додаток 6 test.html', 'r', encoding='utf-8', errors='surrogateescape') as f:
            text = f.read()

        # 1. Add dragging handlers to JS block
        dd_functions = """
        let draggedItem = null;

        function dragStart(e, type, rIdx, iIdx = null, cIdx = null) {
            draggedItem = { type, rIdx, iIdx, cIdx };
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData("text/plain", JSON.stringify(draggedItem));
            
            // Optional: slight opacity to show it's dragging
            setTimeout(() => { e.target.classList.add('opacity-40'); }, 0);
        }

        function allowDrop(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
        }

        function drop(e, targetType, targetRIdx, targetIIdx = null, targetCIdx = null) {
            e.preventDefault();
            e.stopPropagation();
            
            // Remove opacity classes from all
            document.querySelectorAll('.opacity-40').forEach(el => el.classList.remove('opacity-40'));

            if (!draggedItem) return;
            const source = draggedItem;
            
            // Prevent dropping onto itself or its own children
            if (source.rIdx === targetRIdx && source.iIdx === targetIIdx && source.cIdx === targetCIdx) return;
            if (source.type === 'item' && targetType === 'child' && source.rIdx === targetRIdx && source.iIdx === targetIIdx) return;
            
            let objToMove;
            // Extract from source
            if (source.type === 'rop') {
                objToMove = currentRopData.splice(source.rIdx, 1)[0];
            } else if (source.type === 'item') {
                objToMove = currentRopData[source.rIdx].items.splice(source.iIdx, 1)[0];
            } else if (source.type === 'child') {
                objToMove = currentRopData[source.rIdx].items[source.iIdx].children.splice(source.cIdx, 1)[0];
            }

            // Adjust targets if they were shifted by the extraction within the same parent
            if (source.type === 'rop' && targetType === 'rop' && source.rIdx < targetRIdx) { targetRIdx--; }
            if (source.type === 'item' && targetType === 'item' && source.rIdx === targetRIdx && source.iIdx < targetIIdx) { targetIIdx--; }
            if (source.type === 'child' && targetType === 'child' && source.rIdx === targetRIdx && source.iIdx === targetIIdx && source.cIdx < targetCIdx) { targetCIdx--; }

            // Insert into target
            if (source.type === 'rop' && targetType === 'rop') {
                currentRopData.splice(targetRIdx, 0, objToMove);
            } 
            else if (source.type === 'item') {
                if (targetType === 'rop') {
                    if (!currentRopData[targetRIdx].items) currentRopData[targetRIdx].items = [];
                    currentRopData[targetRIdx].items.push(objToMove);
                } else if (targetType === 'item') {
                    currentRopData[targetRIdx].items.splice(targetIIdx, 0, objToMove);
                } else if (targetType === 'child') {
                    currentRopData[targetRIdx].items.splice(targetIIdx, 0, objToMove);
                }
            }
            else if (source.type === 'child') {
                if (targetType === 'child') {
                    currentRopData[targetRIdx].items[targetIIdx].children.splice(targetCIdx, 0, objToMove);
                } else if (targetType === 'item') {
                    const tItem = currentRopData[targetRIdx].items[targetIIdx];
                    if (tItem.type === 'subRop') {
                        if(!tItem.children) tItem.children = [];
                        tItem.children.push(objToMove);
                    } else {
                        currentRopData[targetRIdx].items.splice(targetIIdx, 0, objToMove);
                    }
                } else if (targetType === 'rop') {
                    if (!currentRopData[targetRIdx].items) currentRopData[targetRIdx].items = [];
                    currentRopData[targetRIdx].items.push(objToMove);
                }
            }

            draggedItem = null;
            syncTextFromRop();
            renderVisualRopHierarchy();
        }

        // Add a global drop handler to handle dropping an item into an empty space
        document.addEventListener('dragend', (e) => {
            document.querySelectorAll('.opacity-40').forEach(el => el.classList.remove('opacity-40'));
        });
        """
        
        # Append dd_functions to the end of script
        if 'function escapeHtml(str) {' in text:
            text = text.replace('function escapeHtml(str) {', dd_functions + '\n        function escapeHtml(str) {')
        
        # 2. Modify renderVisualRopHierarchy components
        
        # Child items (БП in ВОП)
        text = text.replace(
            '<div class="flex items-center gap-2 pl-3 py-1.5 border-l-2 border-indigo-200 dark:border-indigo-800">',
            '<div draggable="true" ondragstart="dragStart(event, \'child\', ${rIdx}, ${iIdx}, ${cIdx})" ondragover="allowDrop(event)" ondrop="drop(event, \'child\', ${rIdx}, ${iIdx}, ${cIdx})" class="flex items-center gap-2 pl-3 py-1.5 border-l-2 border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100/50 cursor-grab active:cursor-grabbing transition-colors duration-200">'
        )
        
        # Direct items
        text = text.replace(
            '<div class="flex items-center gap-2 p-2.5 rounded-xl bg-amber-50/40 dark:bg-amber-950/10 border-l-4 border-amber-500 dark:border-amber-600 border-y border-r border-amber-100 dark:border-amber-900/30 my-2">',
            '<div draggable="true" ondragstart="dragStart(event, \'item\', ${rIdx}, ${iIdx})" ondragover="allowDrop(event)" ondrop="drop(event, \'item\', ${rIdx}, ${iIdx})" class="flex items-center gap-2 p-2.5 rounded-xl bg-amber-50/40 dark:bg-amber-950/10 border-l-4 border-amber-500 dark:border-amber-600 border-y border-r border-amber-100 dark:border-amber-900/30 my-2 cursor-grab active:cursor-grabbing hover:-translate-y-0.5 hover:shadow-md transition-all duration-300">'
        )
        
        # SubRop items (ВОП)
        text = text.replace(
            '<div class="bg-indigo-50/40 dark:bg-indigo-950/20 p-3 rounded-xl border-l-4 border-indigo-500 dark:border-indigo-600 border-y border-r border-indigo-100 dark:border-indigo-900/40 space-y-2.5 my-2">',
            '<div draggable="true" ondragstart="dragStart(event, \'item\', ${rIdx}, ${iIdx})" ondragover="allowDrop(event)" ondrop="drop(event, \'item\', ${rIdx}, ${iIdx})" class="bg-indigo-50/40 dark:bg-indigo-950/20 p-3 rounded-xl border-l-4 border-indigo-500 dark:border-indigo-600 border-y border-r border-indigo-100 dark:border-indigo-900/40 space-y-2.5 my-2 cursor-grab active:cursor-grabbing hover:-translate-y-0.5 hover:shadow-md transition-all duration-300">'
        )
        
        # Main ROP Card container (we need to inject attributes into card)
        # Search for:
        # const card = document.createElement('div');
        # card.className = "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden transition-all hover:border-blue-300 dark:hover:border-blue-700";
        
        target_str = 'card.className = "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden transition-all hover:border-blue-300 dark:hover:border-blue-700";'
        replacement_str = target_str + """
                card.setAttribute('draggable', 'true');
                card.setAttribute('ondragstart', `dragStart(event, 'rop', ${rIdx})`);
                card.setAttribute('ondragover', 'allowDrop(event)');
                card.setAttribute('ondrop', `drop(event, 'rop', ${rIdx})`);
                card.classList.add('cursor-grab', 'active:cursor-grabbing', 'hover:-translate-y-1', 'hover:shadow-lg');
        """
        text = text.replace(target_str, replacement_str)

        # 3. Enhance micro-animations
        
        # Add transition to switchRopMode containers
        # `<div id="rop-visual-view" class="space-y-4">` -> `<div id="rop-visual-view" class="space-y-4 transition-opacity duration-300">`
        # wait, it uses `.hidden`. It's hard to animate `display: none` in Tailwind without complex plugins, so we just stick to existing visibility toggle, or we can use opacities. Let's just enhance the button hovers.
        
        # "Додати РОП" button enhancement
        text = text.replace(
            'class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-1.5 px-3 rounded-lg shadow-sm transition-all flex items-center gap-1.5 active:scale-95"',
            'class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-1.5 px-3 rounded-lg shadow-sm hover:shadow-md transition-all duration-300 ease-in-out hover:-translate-y-0.5 flex items-center gap-1.5 active:scale-95"'
        )
        
        # Write back to file
        with open('Додаток 6 test.html', 'w', encoding='utf-8', errors='surrogateescape') as f:
            f.write(text)
            
        print("Successfully applied Drag & Drop and Animation enhancements!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
