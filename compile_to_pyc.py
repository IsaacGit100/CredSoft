import os
import shutil
import subprocess
import sys

DIST = 'dist_pyc'
SOURCE_ROOT = os.getcwd()  # current directory (should be project root)

# ---------- Clean old build ----------
if os.path.exists(DIST):
    shutil.rmtree(DIST)

# ---------- Copy entire project, excluding unwanted ----------
shutil.copytree('.', DIST, ignore=shutil.ignore_patterns(
    '__pycache__', '*.pyc', '.git', 'venv', 'backups', 'media', 'logs', 'dist_pyc', 'static', 'media'
))

# ---------- Compile all .py files with detailed output ----------
print("Compiling all .py files... (this may take a moment)")
result = subprocess.run(
    [sys.executable, '-m', 'compileall', '-b', '-f', '-q', '0', DIST],
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print("Compilation errors detected. The script will continue, but some modules may be missing.")
    print(result.stdout)
    print(result.stderr)
else:
    print("Compilation completed successfully.")

# ---------- Remove .py files (keep __init__.py and manage.py) ----------
print("Removing source .py files...")
for root, dirs, files in os.walk(DIST):
    for file in files:
        if file.endswith('.py') and file not in ['__init__.py', 'manage.py']:
            os.remove(os.path.join(root, file))
    # Remove any __pycache__ folders
    if '__pycache__' in dirs:
        shutil.rmtree(os.path.join(root, '__pycache__'))

# ---------- Ensure every folder that contains a .pyc has an __init__.py ----------
print("Ensuring __init__.py in all package directories...")
for root, dirs, files in os.walk(DIST):
    # Check if this folder contains any .pyc files (i.e., it's a package)
    has_pyc = any(f.endswith('.pyc') for f in files)
    if has_pyc:
        init_file = os.path.join(root, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# package marker')
                print(f"Created missing {init_file}")

# ---------- Detect the project folder (the one containing settings.pyc) ----------
project_folder = None
for item in os.listdir(DIST):
    item_path = os.path.join(DIST, item)
    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'settings.pyc')):
        project_folder = item
        break

if not project_folder:
    # Fallback: assume the first subdirectory that is not a known non‑project folder
    for item in os.listdir(DIST):
        if os.path.isdir(os.path.join(DIST, item)) and item not in ['templates', 'static', 'media']:
            project_folder = item
            break

if project_folder:
    # Ensure __init__.py exists inside the project folder
    init_file = os.path.join(DIST, project_folder, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# package marker')
    # Update manage.py
    manage_path = os.path.join(DIST, 'manage.py')
    if os.path.exists(manage_path):
        with open(manage_path, 'r') as f:
            content = f.read()
        import re
        new_content = re.sub(
            r"os\.environ\.setdefault\(['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"](.*?)['\"]\)",
            f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_folder}.settings')",
            content
        )
        with open(manage_path, 'w') as f:
            f.write(new_content)
        print(f"✅ manage.py updated to use settings module '{project_folder}.settings'")
    else:
        print("⚠️ manage.py not found in dist_pyc")
else:
    print("⚠️ Could not detect project folder. Please set PROJECT_FOLDER manually in the script.")

print("\n✅ Compilation complete. To test, run:")
print(f"  cd {DIST}")
print("  python manage.py runserver")