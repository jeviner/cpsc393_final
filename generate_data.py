from pathlib import Path
from matplotlib import image
from matplotlib import pyplot
import numpy as np
import os
import time

data_dir = "Data"
save_to = "data.npz"
labels = ["normal", "pothole"]

def get_last_folder(path):
    path = str(path)
    return path.split('/')[len(path.split('/'))-2:][0]
    
def generate_data():
    img_files = Path(data_dir).rglob('*.jpg')
    all_data = []
    all_labels = []
    
    start = time.time()
    for img_path in img_files:
        img_data = image.imread(img_path)
        
        # Calculate label
        label = get_last_folder(img_path)
        if label in labels:
            label = labels.index(label)
        else:
            print("Invalid label", label)
            continue
        
        # Check shape using first image as truth value
        if len(all_data) > 0 and img_data.shape != all_data[0].shape:
            print("Shape mismatch", img_path, "has shape", img_data.shape)
            continue
        
        all_data.append(img_data)
        all_labels.append(label)
    end = time.time()
    print("Created a dataset of", len(all_data), "images in", str(round(end - start, 2)) + "s")
    data_arr = np.array(all_data)
    labels_arr = np.array(all_labels)
    np.savez(save_to, data_arr, labels_arr)
    print("Saved to " + save_to)
        
# https://machinelearningmastery.com/how-to-load-and-manipulate-images-for-deep-learning-in-python-with-pil-pillow/
def main():
    generate_data()

if __name__ == '__main__':
    main()
    