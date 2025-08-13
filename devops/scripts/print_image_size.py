import os
import sys


def print_image_size(path):
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required. Install with: pip install Pillow")
        sys.exit(1)

    if os.path.isdir(path):
        files = sorted(os.listdir(path))
        images = [
            f
            for f in files
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"))
        ]
        if not images:
            print(f"No images found in directory: {path}")
            return
        for img_name in images:
            img_path = os.path.join(path, img_name)
            try:
                with Image.open(img_path) as img:
                    w, h = img.size
                print(f"{img_name}: {w}x{h}")
            except Exception as e:
                print(f"{img_name}: Error reading image ({e})")
    elif os.path.isfile(path):
        try:
            with Image.open(path) as img:
                w, h = img.size
            print(f"{os.path.basename(path)}: {w}x{h}")
        except Exception as e:
            print(f"Error reading image {path}: {e}")
    else:
        print(f"Path not found: {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python print_image_size.py <image_or_directory_path>")
        sys.exit(1)
    print_image_size(sys.argv[1])
