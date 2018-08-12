from __future__ import print_function, division

from keras.datasets import mnist, cifar10
from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Sequential, Model
from keras.optimizers import Adam

import matplotlib.pyplot as plt
import sys
import numpy as np


class VGAN():

    def __init__(self):
        self.img_rows = 28
        self.img_cols = 28
        self.channels = 1
        self.img_shape = (self.img_rows, self.img_cols, self.channels)
        self.dimen=100


        self.optimizer = Adam(0.0002, 0.5)

        self.discriminator = self.build_discriminator()
        self.discriminator.compile(loss='binary_crossentropy', optimizer='optimizer', metrics=['accuracy'])

        self.generator = self.build_generator()



    def build_generator(self):

        model = Sequential()
        model.add(Dense(256, input_dim=self.dimen))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(np.prod(self.img_shape), activation='tanh'))
        model.add(Reshape(self.img_shape))

        model.summary()

        noise = Input(shape=(self.dimen,))
        img = model(noise)
        return Model(noise, img)


    def build_discriminator(self):

        model = Sequential()
        model.add(Flatten(input_shape=self.img_shape))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(256))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(1, activation='sigmoid'))

        model.summary()

        img = Input(shape=self.img_shape)
        valid = model(img)

        return Model(img, valid)

    def train(self, epochs, batch_size=64, sample_size=50):

        # load mnist data
        (X_train, _), (_, _) = mnist.load_data()

        # Rescale -1 to 1
        X_train = X_train/127.5 - 1
        X_train = np.expand_dims(X_train, axis=3)

        # adversial ground truth
        valid = np.ones(batch_size, 1)
        fake = np.zeros(batch_size, 1)
        for epoch in range(epochs):

            # Training discriminator
            ids = np.random.randint(0, X_train.shape[0], batch_size)
            imgs = X_train[ids]

            noise = np.random.normal(0, 1, (batch_size, self.dimen))

            # Generate new images
            generate_img = self.generator.predict(noise)

            # train
            dis_loss_real = self.discriminator.train_on_batch(imgs, valid)
            dis_loss_fake = self.discriminator.train_on_batch(generate_img, fake)

            dis_loss = np.add(dis_loss_real, dis_loss_fake)


            # Training generator
            noise = np.random.normal(0, 1, (batch_size, self.dimen))

            # train generator
            gen_loss = self.generator.train_on_batch(noise, valid)

            print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, dis_loss[0], 100*dis_loss[1], gen_loss))

            if epoch % sample_size == 0:
                self.sample_images(epoch)








if __name__ == "__main__":
    vgan = VGAN()
    vgan.train(epochs=500, batch_size=64,sample_size=50)