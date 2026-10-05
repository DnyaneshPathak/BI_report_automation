import os

def check_conflicts(dir_path):
    conflicts = []
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.endswith(('.py', '.html', '.js', '.css', '.md')):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        if '<<<<<<< HEAD' in file.read():
                            conflicts.append(path)
                except:
                    pass
    return conflicts

print(check_conflicts('.'))
