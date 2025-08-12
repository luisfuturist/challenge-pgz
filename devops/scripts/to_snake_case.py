import os
import re
import sys


def to_snake_case(name):
    # Replace hyphens and spaces with underscores
    name = re.sub(r"[-\s]+", "_", name)
    # Convert CamelCase or PascalCase to snake_case
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    # Lowercase everything
    name = name.lower()
    # Remove leading/trailing underscores
    name = name.strip("_")
    # Collapse multiple underscores
    name = re.sub(r"__+", "_", name)
    return name


def process_dir(dirpath):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        # Rename files
        for filename in files:
            old_path = os.path.join(root, filename)
            new_filename = to_snake_case(filename)
            new_path = os.path.join(root, new_filename)
            if old_path != new_path:
                if os.path.exists(new_path):
                    print(f"Cannot rename {old_path} to {new_path}: target exists.")
                else:
                    os.rename(old_path, new_path)
        # Rename directories
        for dirname in dirs:
            old_dir = os.path.join(root, dirname)
            new_dirname = to_snake_case(dirname)
            new_dir = os.path.join(root, new_dirname)
            if old_dir != new_dir:
                if os.path.exists(new_dir):
                    print(f"Cannot rename {old_dir} to {new_dir}: target exists.")
                else:
                    os.rename(old_dir, new_dir)


def process_file(filepath):
    dirpath, filename = os.path.split(filepath)
    new_filename = to_snake_case(filename)
    new_path = os.path.join(dirpath, new_filename)
    if filepath != new_path:
        if os.path.exists(new_path):
            print(f"Cannot rename {filepath} to {new_path}: target exists.")
        else:
            os.rename(filepath, new_path)


def main():
    if len(sys.argv) != 2:
        print("Usage: to_snake_case.py <dirpath|filepath>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        sys.exit(1)
    if os.path.isdir(path):
        process_dir(path)
    else:
        process_file(path)


if __name__ == "__main__":
    main()
