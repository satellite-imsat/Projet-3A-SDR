# Projet-3A-SDR

Contributors :
* Thomas Aussagues
* Arthur Docquois
* Aurélien Gossse 
* Selman Sezguin

### Contact :
* firstname.lastname@imt-atlantique.net

The branch "signal-processing" contains python scripts and functions to illustrate the modulation and demodulation of signals. We focus on assessing the performance of multiple demodulation algorithms for GMSK modulated AIS signals transmitted over a AWGN channel.

### User Guide
1) First clone the repository and install all the required packages :\
    `pip install -r requirements.txt`
    
2) To simulate the transmission of a GMSK modulated binary signal over a additive white gaussian noise channel, run `demo_gmsk_demodulation.py`.
    ````
    >>> python demo_gmsk_demodulation.py
    >>>  ************************************************************
          For a SNR of 10 dB, we have a BER of 0.00392156862745098

         ************************************************************ 
    ````
    
   The generated figures are stored in the `figures` folder. The computed BER is displayed in the terminal.
    
3) To simulate the performance of GMSK (with AIS parameters) over an dditive white gaussian noise channel for different time-bandwidth product values, run `test_gmsk_performance_awgn.py`. It generates multiple Binary Error Rate vs. SNR curves : one for each time-bandwidth product value. Again, the figure is stored in the `figures` folder.

    ````
    python demo_gmsk_demodulation.py
    ````


### References :

[1] Mathuranathan Viswanathan, Digital Modulations using Python, December 2019

[2] Wikipedia contributors. (2022, September 29). Automatic identification system. In Wikipedia, The Free Encyclopedia. Retrieved 19:56, October 25, 2022, from https://en.wikipedia.org/w/index.php?title=Automatic_identification_system&oldid=1113130240

[3] MathWorks, (2022). Communications Toolbox: User's Guide (R2012a). Retrieved October 25, 2022 from https://fr.mathworks.com/help/comm/ug/ship-tracking-using-ais-signals.html
