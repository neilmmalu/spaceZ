Project completed using python3.

Libraries used:
    PyQt5			<= pip install PyQt5
    configParser
    zmq				<= pip install zmq
    numpy			<= pip install numpy==1.19.3
    PIL				<= pip install pillow

To run the program:
    python dsn.py or python3 dsn.py

Format for config files:

[LAUNCH_INFO]
name =                  #Name of launch vehicle
orbit =                 #Orbit in km
payloadConfig =         #Path to payload attached to this vehicle

[PAYLOAD_INFO]
name =                  #Name of payload
type =                  #Type of payload is Comm, Scientific or Spy
time =                  #Frequency of sending data in seconds



GUI Instructions:

    1. First add new launch - only then will commands work

    2. Sometimes, clicking on a button will highlight it blue (this means the GUI is trying to acquire the mutex).
    Click it again (program isn't hung)

    3. p1.ini, p2.ini and p3.ini are the payload files of different types (Scientific, Comm and Image)

    4. Launch can only be created with an lv ini file. 



Assumptions made:
    1. Payload config files cannot be used for a new launch.

    2. Launch vehicle cannot be deorbited before payload is deployed.

    3. Payload cannot be decommissioned before it is deployed.

    4. Payload telemetry data and launch vehicle telemetry are random values not linked to each other. Altitude is assumed to be random, and not linked to orbit

    5. Payload data is randomly generated data.

    6. Images are randomly generated using numpy arrays. Images are not persistent. They are created on the fly, and displayed, then deleted, never saved.
