import os
import re

base_dir = r"C:\Users\Rahul\AppData\Local\Programs\Python\Python313\Lib\site-packages\django"
abc_types = {
    'Iterator', 'Iterable', 'Mapping', 'Sequence', 'Callable', 
    'MutableMapping', 'MutableSequence', 'MutableSet', 'Set', 
    'ItemsView', 'ValuesView', 'KeysView', 'MappingView'
}

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    new_content = content
    
    # Replace collections.Type with collections.abc.Type
    for t in abc_types:
        new_content = re.sub(rf'\bcollections\.{t}\b', f'collections.abc.{t}', new_content)
    
    # Replace from collections import ...
    def sub_from(match):
        imported_names = [n.strip() for n in match.group(1).split(',')]
        from_coll = [n for n in imported_names if n not in abc_types]
        from_abc = [n for n in imported_names if n in abc_types]
        
        lines = []
        if from_coll:
            lines.append(f"from collections import {', '.join(from_coll)}")
        if from_abc:
            lines.append(f"from collections.abc import {', '.join(from_abc)}")
        return '\n'.join(lines)

    new_content = re.sub(r'from collections import ([^(\r\n]*)', sub_from, new_content)

    if new_content != content:
        print(f"Patching {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if filename.endswith('.py'):
            patch_file(os.path.join(root, filename))
