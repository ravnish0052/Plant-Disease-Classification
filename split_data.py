import os
import shutil
import random
from tqdm import tqdm  # Optional, for progress bar

# Define paths
source_dir = 'raw_data'  # Directory where you unzipped the dataset
target_dir = 'PlantVillage'
train_ratio = 0.8  # 80% for training
test_ratio = 0.2  # 20% for testing

# Create train and test folders
os.makedirs(os.path.join(target_dir, 'train'), exist_ok=True)
os.makedirs(os.path.join(target_dir, 'test'), exist_ok=True)

# Function to split and move images
def split_and_move_images(class_name):
    # Get all images in the class directory
    images = os.listdir(os.path.join(source_dir, class_name))
    random.shuffle(images)  # Shuffle images randomly

    # Calculate the split index
    train_idx = int(len(images) * train_ratio)

    # Split images into train and test
    train_images = images[:train_idx]
    test_images = images[train_idx:]

    # Copy images to target directories
    for img in tqdm(train_images, desc=f"Processing {class_name} (train)"):
        src = os.path.join(source_dir, class_name, img)
        dest = os.path.join(target_dir, 'train', class_name)
        os.makedirs(dest, exist_ok=True)
        shutil.copy(src, dest)
    
    for img in tqdm(test_images, desc=f"Processing {class_name} (test)"):
        src = os.path.join(source_dir, class_name, img)
        dest = os.path.join(target_dir, 'test', class_name)
        os.makedirs(dest, exist_ok=True)
        shutil.copy(src, dest)

# Process each class folder
for class_name in os.listdir(source_dir):
    class_path = os.path.join(source_dir, class_name)
    if os.path.isdir(class_path):  # Ensure it's a directory
        split_and_move_images(class_name)

print("Dataset has been organized into train and test folders.")
