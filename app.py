import os
import shutil
import exifread
from datetime import datetime
import yaml
# import pyheif

# Disable to only print out the results.
ENABLE_FILE_COPY = True

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

source_dir = config.get('source')
dest_dir = config.get('destination')

# Define image file extensions to look for
image_extensions = ['.jpg', '.jpeg', '.png', '.heic', '.mov', '.mp4']


def process_file(src_path):
    # Get file extension and check if it's an image file
    file_ext = os.path.splitext(src_path)[1].lower()
    if file_ext not in image_extensions:
        print(f"File extension not supported : {src_path}")
        return

    # Extract the creation date and time from the file
    if file_ext in ['.heic', '.mov', '.mp4']:
        with open(src_path, 'rb') as f:
            # heif_file = pyheif.read_heif(f)
            # tags = heif_file.get_metadata('Exif')[0]
            # create_date = datetime.strptime(tags['DateTimeOriginal'].decode('utf-8'), '%Y:%m:%d %H:%M:%S')
            create_date = datetime.fromtimestamp(os.path.getmtime(src_path))
    else:
        with open(src_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if 'EXIF DateTimeOriginal' in tags:
                create_date = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
            else:
                create_date = datetime.fromtimestamp(os.path.getmtime(src_path))

    # Create destination directory structure based on image creation date
    dest_subdir = os.path.join(dest_dir, create_date.strftime('%Y\%Y%m%d'))
    os.makedirs(dest_subdir, exist_ok=True)

    # Create destination file name based on image creation date and time
    dest_filename = create_date.strftime('%Y%m%d_%H%M%S') + file_ext
    dest_path = os.path.join(dest_subdir, dest_filename)

    # Copy the file to the destination directory if it doesn't already exist
    if not os.path.exists(dest_path):
        if ENABLE_FILE_COPY:
            shutil.copy2(src_path, dest_path)
        print(f"Copied '{src_path}' to '{dest_path}'")
    else:
        print(f"Skipped '{src_path}' (file already exists)")


# Recursively traverse the source directory and process each file
for root, dirs, files in os.walk(source_dir):
    for file in files:
        src_path = os.path.join(root, file)
        process_file(src_path)
