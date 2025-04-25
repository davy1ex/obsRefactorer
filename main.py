import os
import shutil
import re
from datetime import datetime

# === CONFIG ===
# Folders to scan and move files between
ARCHIVE_FOLDER_NAME = "04_archive"
REFERENCES_FOLDER_NAME = "03_references"
MOVEMENT_LOG_FILE = 'movement_history.txt'


# Function to extract all wiki links
def extract_wiki_links(file_path):
    wiki_link_pattern = re.compile(r'!?\[\[([^|\]]+)(?:\|[^]]*)?\]\]')
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return wiki_link_pattern.findall(content)


# Collecting all markdown files in the folder
def collect_markdown_files(folder):
    md_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files


# Get all subfolders in the specified folder
def list_all_subfolders(folder):
    subfolders = []
    for root, dirs, _ in os.walk(folder):
        for d in dirs:
            subfolders.append(os.path.join(root, d))
    return subfolders


# Choose the target directory for moving
def choose_target_directory(default_path, all_dirs):
    print("\nChoose a folder to move the file to:")
    print(f"[0] (default) {default_path}")
    for idx, path in enumerate(all_dirs[:20], 1):  # up to 20 options
        print(f"[{idx}] {path}")
    print(f"[{len(all_dirs)+1}] Enter the path manually")

    choice = input("Your choice (Enter = 0 or path manually): ").strip()

    if choice == "":
        return default_path

    # if the input is a non-digit string
    if not choice.isdigit():
        return choice  # Simply return the input as it is

    idx = int(choice)
    if idx == 0:
        return default_path
    elif 1 <= idx <= len(all_dirs):
        return all_dirs[idx - 1]
    elif idx == len(all_dirs) + 1:
        return input("Enter the path manually: ").strip()
    else:
        print("❌ Invalid choice. Using the default path.")
        return default_path


# Function to log the movements with error handling for encoding
def log_movement(file_name, source_path, target_path):
    try:
        with open(MOVEMENT_LOG_FILE, 'a', encoding='utf-8', errors='replace') as log_file:
            log_file.write(f"{datetime.now()} - Moved: {file_name}\n"
                           f"  Source path: {source_path}\n"
                           f"  Target path: {target_path}\n"
                           f"  Rollback command: mv {target_path} {source_path}\n\n")
            print(f"✅ Log saved: {file_name}")
    except Exception as e:
        print(f"❌ Error writing to log: {e}")


# Moving a file and updating its path with enhanced error handling
def move_asset_interactive(file_name, md_path, references_folder, archive_folder):
    # First, search for the file within the entire 03_references folder (not just assets)
    src = None
    for root, dirs, files in os.walk(references_folder):
        if file_name in files:
            src = os.path.join(root, file_name)
            break

    # If the file is not found, try to find it in the archive folder
    if not src:
        src = os.path.join(archive_folder, file_name)

    # Default path for moving the file
    default_dst = os.path.join(os.path.dirname(md_path), file_name)

    if not os.path.exists(src):
        print(f"⛔ File not found: {file_name}")
        return

    print(f"\n🔍 File found: {src}")
    print(f"📄 In note: {md_path}")
    print(f"📁 Default path: {default_dst}")

    # List all subfolders within the archive folder
    all_folders = list_all_subfolders(archive_folder)
    
    # Allow manual directory selection if needed
    target_dir = choose_target_directory(os.path.dirname(default_dst), all_folders)

    # Check permissions to create the folder
    try:
        os.makedirs(target_dir, exist_ok=True)
    except PermissionError:
        print(f"❌ Error: No permission to create folder in {target_dir}. Try selecting a different folder.")
        return
    except Exception as e:
        print(f"❌ Error creating folder {target_dir}: {e}")
        return

    dst = os.path.join(target_dir, file_name)

    # If the file already exists, skip it
    if os.path.exists(dst):
        print(f"⚠️ File already exists in {dst}, skipping")
        return

    # Move the file to the target directory
    try:
        shutil.move(src, dst)
        print(f"✅ Moved: {file_name} → {dst}")
    except Exception as e:
        print(f"❌ Error moving file: {e}")
        return

    # Log the movement
    log_movement(file_name, src, dst)


# === CONFIG ===
# Function to get the correct vault path
def get_correct_vault_path():
    while True:
        vault_path = input("Enter the path to the root of your Obsidian vault (e.g., ./obsidian): ").strip()
        if not vault_path.startswith('./') and not vault_path.startswith('obsidian'):
            print("❌ The path should start with './' or 'obsidian/'. Try again.")
        elif not os.path.exists(vault_path):
            print("❌ Path not found. Try again.")
        else:
            return vault_path


vault_path = get_correct_vault_path()  # Input with validation

# Set folder paths
archive_folder = os.path.join(vault_path, ARCHIVE_FOLDER_NAME)
references_folder = os.path.join(vault_path, REFERENCES_FOLDER_NAME)

# Collect the list of all markdown files IN ADVANCE
markdown_files = collect_markdown_files(archive_folder)


def count_files_in_vault(vault_path):
    total_files = 0
    for root, _, files in os.walk(vault_path):
        total_files += len(files)
    return total_files


if __name__ == "__main__":
    initial_file_count = count_files_in_vault(vault_path)
    print(f"🗃️ The vault contains {initial_file_count} files at the beginning.")

    markdown_files = collect_markdown_files(archive_folder)

    for md_path in markdown_files:
        print(f"\n📄 Processing file: {md_path}")
        links = extract_wiki_links(md_path)
        print("🔗 Found links:", links)

        for link in links:
            move_asset_interactive(link, md_path, references_folder, archive_folder)

    final_file_count = count_files_in_vault(vault_path)
    print(f"\n🗃️ The vault contains {final_file_count} files after processing.")

    # Print the difference
    if final_file_count == initial_file_count:
        print("🔎 The number of files has not changed.")
    else:
        print(f"📉 The number of files changed by {initial_file_count - final_file_count}.")
