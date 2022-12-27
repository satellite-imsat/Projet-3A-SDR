import numpy as np


def awgn_channel(v_signal : np.ndarray, snr_db : float):

    '''Thif function simulates the propagation of a signal through an Additive White Gaussian Noise
    channel. The noise power is computed such that the output signal has the specified SNR value in
    dB.
    
    Inputs :
    
    -> v_signal      :
    -> snr_db        :

    Output :
    
    -> v_signal_awgn :
    
    '''

    # Here, we consider a simple AWGN channel with no attenuation
    # First we get the signal power defined as the signal squared norm divided by the number of symbols
    signal_power = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]

    # Then, we compute the noise power (in linear units) by applying the SNR definition in linear units.
    noise_power = signal_power / (10 ** (snr_db / 10))
    
    # Finally, we simply add a random complex noise to the signal since we have an AWGN channel.
    v_signal_awgn = v_signal + np.sqrt(noise_power / 2) * (np.random.randn(v_signal.shape[0]) \
        + 1j * np.random.randn(v_signal.shape[0]))

    return v_signal_awgn