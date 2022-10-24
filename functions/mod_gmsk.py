
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt

from functions.gen_signal import binary_to_nrz_signal

def gaussian_filter(time_bandwidth_product : float, tb : float, up_sampling_factor : int, filter_length : int):

    b = time_bandwidth_product / tb

    sigma_squared = np.log(2) / (2 * np.pi * b) ** 2

    v_time = np.arange(start = - filter_length * tb, stop = filter_length * tb + tb / up_sampling_factor, step = tb / up_sampling_factor)

    v_impulse_response = 1 / np.sqrt(2 * np.pi * sigma_squared) * np.exp(- v_time ** 2 / (2 * sigma_squared))

    v_impulse_response /= np.sum(v_impulse_response)

    return v_impulse_response

def mod_signal_gmsk(v_signal : np.ndarray, fc : float, up_sampling_factor : int, time_bandwidth_product : float, modulation_index = 0.5, filter_length = 1) -> np.ndarray:

    fs = up_sampling_factor * fc
    ts = 1 / fs
    tb = up_sampling_factor * ts

    v_signal = v_signal.squeeze()

    n_symb = v_signal.shape[0]

    # NRZ conversion 
    v_signal = binary_to_nrz_signal(binary_signal = v_signal, up_sampling_factor = up_sampling_factor)
    #print(v_signal[:10])
    v_gaussian_filter = gaussian_filter(time_bandwidth_product = time_bandwidth_product, tb = tb, up_sampling_factor = up_sampling_factor, filter_length = filter_length).squeeze()
    v_signal = np.convolve(a = v_signal, v = v_gaussian_filter, mode = "full")
    
    # Normalisation step 
    v_signal /= np.max(v_signal)
    v_signal = scipy.signal.lfilter(b = [1], a = [1, -1], x = v_signal * 1 / fs)
    
    v_signal *= np.pi * 0.5 / tb
    
    v_i_signal = np.cos(v_signal)
    v_q_signal = np.sin(v_signal)
    
    #v_time = np.arange(start = 0, stop = n_symb, step = 1) / fs

    #plt.figure()
    #plt.plot(v_i_signal, v_q_signal)
    #plt.show()


    #print(v_i_signal.shape, v_time.shape)
    #gmsk_signal = v_i_signal - v_q_signal
    gmsk_signal = v_i_signal - 1j *  v_q_signal
   # gmsk_signal *= np.exp(2 * 1j * np.pi * v_time * fc)


    return gmsk_signal

def demod_gmsk(v_signal : np.ndarray, fc : float, up_sampling_factor : int) -> np.ndarray :

    n_ech = v_signal.shape[0]
    #print(n_ech)
    v_time = np.arange(start = 0, stop = n_ech, step = 1) / (fc * up_sampling_factor)
    #v_signal = v_signal * np.exp( -2 * 1j * np.pi * fc * v_time)

    v_i_signal = np.real(v_signal)
    v_q_signal = - np.imag(v_signal)

    v_i_signal_delayed = np.hstack((np.zeros(up_sampling_factor), v_i_signal[0 : n_ech - up_sampling_factor]))
    v_q_signal_delayed = np.hstack((np.zeros(up_sampling_factor), v_q_signal[0 : n_ech - up_sampling_factor]))

    signal_hat = v_q_signal * v_i_signal_delayed - v_i_signal * v_q_signal_delayed

    
    signal_hat = (signal_hat[2*up_sampling_factor-1:-up_sampling_factor:up_sampling_factor] > 0).astype(int)
    #print('signal hat shape', signal_hat)
    return signal_hat

