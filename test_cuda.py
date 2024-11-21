import tensorflow as tf

print("TensorFlow version:", tf.__version__)

if tf.config.list_physical_devices('GPU'):
    print("GPUs detected:", tf.config.list_physical_devices('GPU'))
else:
    print("No GPUs detected")
