# Projet-3A-SDR

Contributors :
* Thomas Aussagues
* Arthur Docquois
* Aurélien Gossse 
* Selman Sezguin

### Description
This code provides a Python implementation of an AIS packet generator, by following the steps given in the paper of 
Andis Dembovskis (see reference [1]). 

### User Guide
1) First clone the repository and install all the required packages :\
    `pip install -r requirements.txt`
2) To run the tests :\
    `pytest ais_generator_test.py`
3) To get an AIS packet from an AIVDM/AIVDO message :
    ````
   >>> from ais_generator import get_ais_packet
   
   >>> ais_msg = '!AIVDM,1,1,,B,19NS7Sp02wo?HETKA2K6mUM20<L=,0*27'
   
   >>> ais_data_bit = get_ais_packet(ais_msg)
   >>> print(ais_data_bit)
   [1 0 1 0 1 0 1 0 1 1 0 0 1 1 0 0 1 1 0 0 1 1 0 0 1 1 0 0 1 1 0 0 1 1 1 1 1
    1 1 0 1 0 0 1 0 1 0 1 1 1 1 0 0 1 0 0 0 0 1 0 1 1 0 0 1 1 1 1 1 0 1 0 1 1
    1 1 1 1 0 1 0 1 0 1 0 1 0 1 0 0 0 1 1 0 1 0 1 1 0 0 0 0 0 0 1 1 1 1 1 1 0
    1 0 0 0 0 1 0 1 0 0 0 1 1 0 1 1 1 0 0 1 1 1 0 0 0 1 0 1 0 1 1 0 1 0 0 1 0
    0 0 1 0 0 1 0 1 1 1 0 1 0 0 0 1 1 1 0 0 1 1 1 1 1 1 0 1 1 0 0 1 0 0 1 0 1
    0 0 1 0 1 0 1 0 1 0 1 1 1 1 0 1 0 0 0 0 1 1 1 0 1 0 1 1 0 1 1 1 0 1 1 0 1
    1 0 1 0 1 0 1 1 1 1 1 1 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
    0]
   ````