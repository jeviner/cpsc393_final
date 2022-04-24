from pathlib import Path
from PIL import Image
import os
import time
import imagehash
import numpy as np

data_dir = "RawData"
out_dir = "Data"

# quality: The image quality, on a scale from 1 (worst) to
# 95 (best). The default is 75. Values above 95 should be
# avoided; 100 disables portions of the JPEG compression
# algorithm, and results in large files with hardly any
# gain in image quality.
img_quality = 75
width = 64
height = width  # square
mode = "RGB"  # https://pillow.readthedocs.io/en/stable/handbook/concepts.html

print_every = 100
crop_before_resize = False
allow_upscale = False
sort_by_last_folder = True

# Helpers

# https://note.nkmk.me/en/python-pillow-image-crop-trimming/


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def shorten_path(path):
    return '/'.join(str(path).split('/')[1:])


def get_output_path(path, in_dir, out_dir):
    path_str = str(path)
    if sort_by_last_folder:
        last_folder = path_str.split('/')[len(path_str.split('/'))-2:][0]
        filename = os.path.basename(path)
        return os.path.join(out_dir, last_folder, filename)
    else:
        return path_str.replace(in_dir, out_dir)

# Processing


def process_img(pil_img):
    img_width = pil_img.size[0]
    img_height = pil_img.size[1]

    if not allow_upscale and (img_width < width or img_height < height):
        return None
    if img_width == width and img_height == height:
        # Image needs no processing
        result = pil_img
    elif crop_before_resize:
        # Crop image to middle square, then resize
        result = crop_max_square(pil_img).resize((width, height))
    else:
        # Resize image
        result = pil_img.resize((width, height))

    # Convert to mode if needed
    if result.mode != mode:
        result = result.convert(mode)
    return result

# Main Operations

# https://medium.com/@somilshah112/how-to-find-duplicate-or-similar-images-quickly-with-python-2d636af9452f


def find_duplicates(img_dir, verbose=True):
    img_files = Path(img_dir).rglob('*.jpg')
    hashes = {}
    duplicates = []
    hash_size = 8

    start = time.time()
    for img_path in img_files:
        with Image.open(img_path) as img:
            short_path = shorten_path(img_path)
            temp_hash = imagehash.average_hash(img, hash_size)
            if temp_hash in hashes:
                if verbose:
                    print(short_path, "is a duplicate of", hashes[temp_hash])
                duplicates.append(img_path)
            else:
                hashes[temp_hash] = short_path
    end = time.time()
    print("Found " + str(len(duplicates)) +
          " duplicates in " + str(round(end - start, 2)) + "s")
    return duplicates


def delete_files(files):
    if len(files) <= 0:
        return 0
    for file_path in files:
        if str(file_path).lower().endswith((".jpg")):
            os.remove(file_path)
        else:
            print(file_path, "is not an image!")
    print("Deleted", len(files), "files")
    return len(files)


def process_all(in_dir, out_dir, verbose=True):
    # If we want to read multiple file types: https://stackoverflow.com/questions/4568580/python-glob-multiple-filetypes
    img_files = Path(in_dir).rglob('*.jpg')

    num_processed = 0
    start = time.time()
    for img_path in img_files:
        #file_name = os.path.basename(img_path)
        img = Image.open(img_path)
        processed_img = process_img(img)
        if processed_img == None:
            # Skip
            continue

        # Compute output path
        output_path = get_output_path(img_path, in_dir, out_dir)
        output_dir = os.path.dirname(output_path)
        # Ensure folder exists
        os.makedirs(output_dir, exist_ok=True)
        # Save file
        processed_img.save(output_path, quality=img_quality)

        num_processed += 1
        if verbose and num_processed % print_every == 0:
            print(num_processed, "images processed")
    end = time.time()

    print("Processed " + str(num_processed) +
          " images in " + str(round(end - start, 2)) + "s")
    return num_processed


def main():
    print("Converting all images in " + data_dir +
          " to " + str(width) + "x" + str(height) + "...")
    num_found = process_all(data_dir, out_dir, verbose=True)
    duplicates = find_duplicates(out_dir, verbose=False)

    print("Deleting duplicate files...")
    num_deleted = delete_files(duplicates)

    print()
    print("Created", num_found - num_deleted,
          "images total in the directory", out_dir)


if __name__ == '__main__':
    main()
