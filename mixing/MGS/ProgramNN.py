from tensorflow.keras import layers
from tensorflow.keras import models
import tensorflow as tf 
from tensorflow import keras

seq_length = 64 

meta_input = layers.Input((seq_length, 3))
note_input = layers.Input((seq_length, 128))

a = layers.Dense(32)(meta_input)
a = layers.Dense(64)(a)
a = models.Model(inputs=meta_input, outputs=a)

b = layers.Dense(32)(note_input)
b = layers.Dense(64)(b)
b = models.Model(inputs=note_input, outputs=b)

combined = layers.concatenate([a.output, b.output])
c = layers.Flatten()(combined)
c = layers.Dense(256)(c)
c = layers.Dense(128, activation='softmax')(c)

model = models.Model(inputs=[meta_input, note_input], outputs=c)

optimizer = tf.keras.optimizers.Adam(learning_rate=0.05)
model.compile(loss=keras.losses.CategoricalCrossentropy(), optimizer=optimizer, metrics=['acc'])
