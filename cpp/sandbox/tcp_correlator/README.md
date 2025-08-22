
This is a test code where the main process is listening to a given port where the data arrived in an interleaved format (R1,I1,R2,I2,...) The expected data is int16.

The receipt data is memcpy to another location and a thread is launch to compute the correlation. A setteable amount of correlations are integrated and sent to another socket.

The raw directory has a hardcoded program where the data is fixed.. its the firts iteration to make the proof of concept.
The raw_cli directory can modify the hyperaparameters to be able to modify the hyperparameters.
The scpi_interface in top of that allows to modify the hyperparameters on the fly (to be done)


