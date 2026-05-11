import os
from pathlib import Path

def create_minivault_structure(base_path: str):
    base = Path(base_path).resolve()
    root = base / "MiniVault"
    
    # Create all directories
    directories = [
        root,
        root / "core",
        root / "ui",
        root / "utils",
        root / "data",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create empty __init__.py files
    init_files = [
        root / "core" / "__init__.py",
        root / "ui" / "__init__.py",
        root / "utils" / "__init__.py",
    ]
    
    for init_file in init_files:
        init_file.touch(exist_ok=True)
        print(f"✅ Created: {init_file.name} in {init_file.parent.name}")
    
    # Create the rest of the files (empty)
    files = [
        root / "main.py",
        root / "core" / "vault.py",
        root / "core" / "note.py",
        root / "ui" / "main_window.py",
        root / "utils" / "config.py",
        root / "data" / "config.ini",
        root / "requirements.txt",
        root / "build.bat",
    ]
    
    for file in files:
        file.touch(exist_ok=True)
        print(f"✅ Created file: {file.name}")
    
    print("\n🎉 MiniVault structure successfully created at:")
    print(root)

# ========================
# RUN THE SCRIPT
# ========================

if __name__ == "__main__":
    target_path = r"C:\Users\Парадокс\Documents\GitHub\obsidian_copy_it"
    
    if not os.path.exists(target_path):
        print("❌ Target folder does not exist!")
        print("Please create it first or change the path.")
    else:
        create_minivault_structure(target_path)