# -*- coding: utf-8 -*-
"""Breast Cancer Image Classification using CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HJZ1uVdt91rg1u98dAJLKAIzP35PS_M6

##Breast Cancer Image Classification using CNN

Dataset tersebut merupakan gambar mikroskopis dengan zoom sebesar 400x pada pasien yang mengalami kanker payudara (Breast Cancer), dimana pada dataset tesebut dibagi menjadi dua kelas yaitu Tumor ganas (Malignant) dan Tumor jinak (Benign). Dataset sudah dibagi menjadi folder training dan testing yang berbeda dengan struktur sebagai berikut:
- BreaKHis 400X/train/benign/*kumpulan gambar
- BreaKHis 400X/train/malignant/*kumpulan gambar
- BreaKHis 400X/test/benign/*kumpulan gambar
- BreaKHis 400X/test/malignant/*kumpulan gambar

---

## Download dan Load Data
"""

from google.colab import drive
from google.colab import files

# Library

from google.colab import drive

# U/ mengorganisir dataset pada folder
import os
import glob
import zipfile
import shutil
import cv2 
import numpy as np
import random

# U/ pemodelan 
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dense, Flatten,Input, Dropout
from tensorflow.keras.layers import GlobalMaxPool2D, AvgPool2D, GlobalAvgPool2D, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
from tensorflow.keras import Model

# U/ visualisasi plot dan report
from keras.preprocessing import image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

import warnings
warnings.filterwarnings( 'ignore')

drive.mount('/content/gdrive')

# Mengatur Directory Konfigurasi
os.environ['KAGGLE_CONFIG_DIR'] = "/content/gdrive/My Drive/Dataset/Kaggle"

# Commented out IPython magic to ensure Python compatibility.
# Masuk Direktori
# %cd /content/gdrive/My Drive/Dataset/Kaggle

files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!ls ~/.kaggle

!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d forderation/breakhis-400x

# ekstrak dataset 
ekstrak_zip = '/content/gdrive/My Drive/Dataset/Kaggle/breakhis-400x.zip'
out_zip = zipfile.ZipFile(ekstrak_zip, 'r')
out_zip.extractall('/content/gdrive/My Drive/Dataset/Modul 2')
out_zip.close()

print('Selesai Ekstrak')

train_benign_dir = "/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/train/benign/"
train_malignant_dir = "/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/train/malignant/"
test_benign_dir = "/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/test/benign/"
test_malignant_dir = "/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/test/malignant/"

print('total training benign images :', len(os.listdir(train_benign_dir)))
print('total training malignant images:', len(os.listdir(train_malignant_dir)))
print('total test benign images:', len(os.listdir(test_benign_dir)))
print('total test malignant images:', len(os.listdir(test_malignant_dir)))

# pengaturan letak folder / dir
benign_dir = os.path.join(train_benign_dir, test_benign_dir)  
malignant_dir = os.path.join(train_malignant_dir, test_malignant_dir)

list1 = [benign_dir,malignant_dir]

fig = plt.figure(figsize=(12, 8))
plt.style.use("ggplot")

j=1
for i in list1: 
    for k in range(4):
        filenames  = os.listdir(i)
        sample = random.choice(filenames)
        image = load_img(i+sample)
        plt.subplot(2,4,j)
        plt.imshow(image)
        plt.xlabel(i.split("/")[-2])
        j+=1
plt.tight_layout()

"""## Preprocessing Data"""

# Gather data train dg image 250x250
training_dir = os.path.join('/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/train')

train_data = []
train_label = []
for r, d, f in os.walk(training_dir):
    for file in f:
        if ".png" in file:
            imagePath = os.path.join(r, file)
            image = cv2.imread(imagePath)
            image = cv2.resize(image, (250,250))
            train_data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            train_label.append(label)

train_data = np.array(train_data)
train_label = np.array(train_label)

print('Selesai Gather Data Train')

# Gather data validation dg image 250x250
validation_dir = os.path.join('/content/gdrive/My Drive/Dataset/Modul 2/BreaKHis 400X/test')

val_data = []
val_label = []
for r, d, f in os.walk(validation_dir):
    for file in f:
        if ".png" in file:
            imagePath = os.path.join(r, file)
            image = cv2.imread(imagePath)
            image = cv2.resize(image, (250,250))
            val_data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            val_label.append(label)

val_data = np.array(val_data)
val_label = np.array(val_label)

print('Selesai Gather Data Validation')

print("Train Data = ", train_data.shape)
print("Train Label = ", train_label.shape)
print("Validation Data = ", val_data.shape)
print("Validation Label = ", val_label.shape)

# Normalisasi data
print("Data sebelum di-normalisasi ", train_data[0][0][0])
x_train = train_data.astype('float32') / 255.0
x_val = val_data.astype('float32') / 255.0
print("Data setelah di-normalisasi ", x_train[0][0][0])

print("Label sebelum di-encoder [0]", train_label[100:105])
print("Label sebelum di-encoder [1]", train_label[995:1000])

lb = LabelEncoder()
y_train = lb.fit_transform(train_label)
y_val = lb.fit_transform(val_label)

print("\nLabel setelah di-encoder [0]", y_train[100:105])
print("Label setelah di-encoder [1]", y_train[995:1000])

"""#Modelling Model 1 (Global Maxpool) dan Model 2 (AveragePool) """

# Model Scenario Pertama

model_1 =  Sequential([
    # Input Layer
    Input(shape=(250,250, 3)),

    # Convolutional layer
    Conv2D(32, (3,3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    GlobalMaxPool2D(),

    # Meratakan input menjadi 1 dimensi
    Flatten(),
    
    #Fully-connected layer
    Dense(128, activation='relu'),
    Dense(1, activation='sigmoid')
])

model_1.summary()

# Model Scenario Kedua

model_2 =  Sequential([
    # Input Layer
    Input(shape=(250,250, 3)),

    # CNN Model 
    Conv2D(32, (3,3), activation='relu'),
    AvgPool2D(pool_size=(2, 2)),
    Conv2D(64, (3,3), activation='relu'),
    AvgPool2D(pool_size=(2, 2)),
    Conv2D(128, (3,3), activation='relu'),
    AvgPool2D(pool_size=(2, 2)),
    GlobalAvgPool2D(),

    # Meratakan input menjadi 1 dimensi
    Flatten(),
    
    #Fully-connected layer
    Dense(128, activation='relu'),
    Dense(1, activation='sigmoid')
])

model_2.summary()

# Compile dengan optimizer adam
Adam(learning_rate=0.00146, name='Adam')
model_1.compile(optimizer = 'Adam',loss = 'binary_crossentropy',metrics = ['accuracy'])
model_2.compile(optimizer = 'Adam',loss = 'binary_crossentropy',metrics = ['accuracy'])

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.9 and logs.get('val_accuracy')>0.9):
      print("\nAkurasi train dan validasi telah mencapai nilai > 90%!")
      self.model.stop_training = True
callbacks = myCallback()

# Training model scenario Pertama
history1 = model_1.fit(x_train, y_train,
                    batch_size=8,
                    steps_per_epoch = len(x_train) // 8,
                    epochs=100,
                    validation_data=(x_val, y_val),
                    callbacks=[callbacks])

# Training model scenario Kedua
history2 = model_2.fit(x_train, y_train,
                    batch_size=8,
                    steps_per_epoch = len(x_train) // 8,
                    epochs=100,
                    validation_data=(x_val, y_val),
                    callbacks=[callbacks])

"""## Plot Accuracy dan Loss Untuk Model 1 dan Model 2"""

# Plot Acc dan Loss

acc1 = history1.history["accuracy"]
val_acc1 = history1.history["val_accuracy"]
acc2 = history2.history["accuracy"]
val_acc2 = history2.history["val_accuracy"]

loss1 = history1.history["loss"]
val_loss1 = history1.history["val_loss"]
loss2 = history2.history["loss"]
val_loss2 = history2.history["val_loss"]

# epochs = range(50)
epochs = range(len(acc1))
epochs2 = range(len(acc2))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[20, 5])
ax1.plot(epochs, acc1, 'r')
ax1.plot(epochs, val_acc1, 'g')
ax1.plot(epochs2, acc2, 'c')
ax1.plot(epochs2, val_acc2, 'y')
ax1.set_title('Model 1 dan Model 2 accuracy')
ax1.legend(['Model 1 accuracy','Model 1 Val accuracy','Model 2 accuracy','Model 2 Val accuracy'])

ax2.plot(epochs, loss1, 'r')
ax2.plot(epochs, val_loss1, 'g')
ax2.plot(epochs2, loss2, 'c')
ax2.plot(epochs2, val_loss2, 'y')
ax2.set_title('Model 1 dan Model 2 loss')
ax2.legend(['Model 1 loss','Model 1 Val loss','Model 2 loss','Model 2 Val loss'])

plt.show()

"""## Percobaan Prediksi"""

uploaded1 = files.upload()

for fn in uploaded1.keys():
 
  # Prediksi Gambar
  path = fn
  img = image.load_img(path, target_size=(250,250))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])

  classes = model_1.predict(images, batch_size=8)
  classes2 = model_2.predict(images, batch_size=8)

  print('Prediksi = ',classes[0][0])
  
  # Prediksi Gambar 
  # Benign 0 - <1 / Malignant >1
  if classes[0][0] >= 0 and classes[0][0] < 1:
    print('\nModel 1, Prediksi Gambar adalah Tumor Jinak (Benign)')
  else:
    print('Model 1, Prediksi Gambar adalah Tumor Ganas (Malignant)')

  if classes2[0][0] >= 0 and classes[0][0] < 1:
    print('Model 2, Prediksi Gambar adalah Tumor Jinak (Benign)')
  else:
    print('Model 2, Prediksi Gambar adalah Tumor Ganas (Malignant)')

uploaded2 = files.upload()

for fn in uploaded2.keys():
 
  # Prediksi Gambar
  path = fn
  img = image.load_img(path, target_size=(250,250))
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])

  classes = model_1.predict(images, batch_size=8)
  classes2 = model_2.predict(images, batch_size=8)

  print('Prediksi = ',classes[0][0])
  
  # Prediksi Gambar 
  # Benign 0 - <1 / Malignant >1
  if classes[0][0] >= 0 and classes[0][0] < 1:
    print('\nModel 1, Prediksi Gambar adalah Tumor Jinak (Benign)')
  else:
    print('Model 1, Prediksi Gambar adalah Tumor Ganas (Malignant)')

  if classes2[0][0] >= 0 and classes[0][0] < 1:
    print('Model 2, Prediksi Gambar adalah Tumor Jinak (Benign)')
  else:
    print('Model 2, Prediksi Gambar adalah Tumor Ganas (Malignant)')

"""##Classification Report dan Accuracy"""

print("model 1")
pred = model_1.predict(x_val)
labels = (pred > 0.5).astype(np.int)

print(classification_report(y_val, labels))

print("model 2")
pred2 = model_2.predict(x_val)
labels2 = (pred2 > 0.5).astype(np.int)

print(classification_report(y_val, labels2))