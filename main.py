import numpy as np
import pickle
import cv2
import os
import matplotlib.pyplot as plt
from os import listdir
from sklearn.preprocessing import LabelBinarizer
from keras.models import Sequential
from keras.layers import BatchNormalization
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Activation, Flatten, Dropout, Dense
from keras import backend as K
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from keras.preprocessing import image
from keras.preprocessing.image import img_to_array
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Input


#Load Dataset
# Initializing a few parameters required for the image dataset preprocessing

# Dimension of resized image
DEFAULT_IMAGE_SIZE = tuple((256, 256))
# Number of images used to train the model
N_IMAGES = 100
# Path to the dataset folder
root_dir = 'PlantVillage'

train_dir = os.path.join(root_dir, 'train')
#val_dir = os.path.join(root_dir, 'val')



#We use the function convert_image_to_array to resize an image to the size DEFAULT_IMAGE_SIZE we defined above.
def convert_image_to_array(image_dir):
    try:
        image = cv2.imread(image_dir)
        if image is not None:
            image = cv2.resize(image, DEFAULT_IMAGE_SIZE)   
            return img_to_array(image)
        else:
            return np.array([])
    except Exception as e:
        print(f"Error : {e}")
        return None
    


#Here, we load the training data images by traversing through all the folders and converting all the images and labels into separate lists respectively.
image_list, label_list = [], []

try:
    print("[INFO] Loading images ...")
    plant_disease_folder_list = listdir(train_dir)

    for plant_disease_folder in plant_disease_folder_list:
        print(f"[INFO] Processing {plant_disease_folder} ...")
        plant_disease_image_list = listdir(f"{train_dir}/{plant_disease_folder}/")

        for image in plant_disease_image_list[:N_IMAGES]:
            image_directory = f"{train_dir}/{plant_disease_folder}/{image}"
            if image_directory.endswith(".jpg")==True or image_directory.endswith(".JPG")==True:
                image_list.append(convert_image_to_array(image_directory))
                label_list.append(plant_disease_folder)

    print("[INFO] Image loading completed")  
except Exception as e:
    print(f"Error : {e}")

# Transform the loaded training image data into numpy array
np_image_list = np.array(image_list, dtype=np.float16) / 225.0
print()

# Check the number of images loaded for training
image_len = len(image_list)
print(f"Total number of images: {image_len}")




#Examine the labels/classes in the training dataset.
label_binarizer = LabelBinarizer()
image_labels = label_binarizer.fit_transform(label_list)

pickle.dump(label_binarizer,open('plant_disease_label_transform.pkl', 'wb'))
n_classes = len(label_binarizer.classes_)

print("Total number of classes: ", n_classes)




#Augment and Split Dataset
#Using ImageDataGenerator to augment data by performing various operations on the training images.
augment = ImageDataGenerator(rotation_range=25, width_shift_range=0.1,
                             height_shift_range=0.1, shear_range=0.2, 
                             zoom_range=0.2, horizontal_flip=True, 
                             fill_mode="nearest")

#Splitting the data into training and test sets for validation purpose.
print("[INFO] Splitting data to train and test...")
x_train, x_test, y_train, y_test = train_test_split(np_image_list, image_labels, test_size=0.2, random_state = 42) 



#Build Model
#Defining the hyperparameters of the plant disease classification model.
EPOCHS = 25
STEPS = 100
LR = 1e-3
BATCH_SIZE = 32
WIDTH = 256
HEIGHT = 256
DEPTH = 3
inputShape = (HEIGHT, WIDTH, DEPTH)
chanDim = -1

#Creating a sequential model and adding Convolutional, Normalization, Pooling, Dropout and Activation layers at the appropriate positions.
model = Sequential([
    Input(shape=inputShape),
    Conv2D(32, (3, 3), padding="same"),
    Activation("relu"),
    BatchNormalization(axis=chanDim),
    MaxPooling2D(pool_size=(3, 3)),
    Dropout(0.25),
    
    Conv2D(64, (3, 3), padding="same"),
    Activation("relu"),
    BatchNormalization(axis=chanDim),
    Conv2D(64, (3, 3), padding="same"),
    Activation("relu"),
    BatchNormalization(axis=chanDim),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),
    
    Conv2D(128, (3, 3), padding="same"),
    Activation("relu"),
    BatchNormalization(axis=chanDim),
    Conv2D(128, (3, 3), padding="same"),
    Activation("relu"),
    BatchNormalization(axis=chanDim),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),
    
    Flatten(),
    Dense(1024),
    Activation("relu"),
    BatchNormalization(),
    Dropout(0.5),
    Dense(n_classes),
    Activation("softmax")
])



model.summary()




#Train Model
#We initialize Adam optimizer with learning rate and decay parameters.
#Also, we choose the type of loss and metrics for the model and compile it for training.

# Initialize optimizer
opt = Adam(learning_rate=LR)

# Compile model
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

# Train model
print("[INFO] Training network...")
history = model.fit(augment.flow(x_train, y_train, batch_size=BATCH_SIZE),
                              validation_data=(x_test, y_test),
                              steps_per_epoch=len(x_train) // BATCH_SIZE,
                              epochs=EPOCHS, 
                              verbose=1)



#Evaluate Model
#Comparing the accuracy and loss by plotting the graph for training and validation.

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)

# Train and validation accuracy
plt.plot(epochs, acc, 'b', label='Training accurarcy')
plt.plot(epochs, val_acc, 'r', label='Validation accurarcy')
plt.title('Training and Validation accurarcy')
plt.legend()

plt.figure()

# Train and validation loss
plt.plot(epochs, loss, 'b', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and Validation loss')
plt.legend()
plt.show()




#Evaluating model accuracy by using the evaluate method
print("[INFO] Calculating model accuracy")
scores = model.evaluate(x_test, y_test)
print(f"Test Accuracy: {scores[1]*100}")






