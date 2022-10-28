import numpy as np



def propagation_loss(v_signal : np.ndarray, tx_power_dB : float, g_tx_dBi, g_rx_dBi, carrier_frequency_Mhz : float, distance_km : float):

    loss_dB = 32.45 + 20 * np.log10(carrier_frequency_Mhz) + 20 * np.log10(distance_km)
    
    rx_power_dB = tx_power_dB + g_tx_dBi + g_rx_dBi - loss_dB

    rx_power_W = 10 ** (rx_power_dB / 10)
    
    # We transform the signal such that its power is rx_power_W
    # We get the signal power
    signal_power_dB = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]
    signal_power_W = 10 ** (signal_power_dB / 10)

    # We divide the signal by its power square root and multiply by the quare root of the desired one. 
    # Remark 1 : note the dB -> W conversion.
    # Remark 2 : we use the power square root since we work with the signal amplitude and not magnitude.
    v_signal = v_signal * (rx_power_W / signal_power_W) ** 0.5

    
    return v_signal

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