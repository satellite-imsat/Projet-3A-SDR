
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

def gmsk_mod(a,fc,L,BT,enable_plot=False):
    """
    Function to modulate a binary stream using GMSK modulation
    Parameters:
        BT : BT product (bandwidth x bit period) for GMSK
        a : input binary data stream (0's and 1's) to modulate
        fc : RF carrier frequency in Hertz
        L : oversampling factor
        enable_plot: True = plot transmitter waveforms (default False)
    Returns:
        (s_t,s_complex) : tuple containing the following variables
            s_t : GMSK modulated signal with carrier s(t)
            s_complex : baseband GMSK signal (I+jQ)
    """
    from scipy.signal import upfirdn,lfilter
    
    fs = L*fc; Ts=1/fs;Tb = L*Ts; # derived waveform timing parameters
    a = 2 * a - 1
    c_t = upfirdn(h=[1]*L, x= a, up = L) #NRZ pulse train c(t)
    
    k=1 # truncation length for Gaussian LPF
    h_t = gaussian_filter(BT,Tb,L,k) # Gaussian LPF with BT=0.25
    b_t = np.convolve(h_t,c_t,'full') # convolve c(t) with Gaussian LPF to get b(t)
    bnorm_t = b_t/max(abs(b_t)) # normalize the output of Gaussian LPF to +/-1
    
    h = 0.5
    # integrate to get phase information
    phi_t = lfilter(b = [1], a = [1,-1], x = bnorm_t*Ts) * h*np.pi/Tb 
    
    I = np.cos(phi_t)
    Q = np.sin(phi_t) # cross-correlated baseband I/Q signals
  
    s_complex = I - 1j*Q # complex baseband representation
    t = Ts* np.arange(start = 0, stop = len(I)) # time base for RF carrier
    sI_t = I*np.cos(2*np.pi*fc*t); sQ_t = Q*np.sin(2*np.pi*fc*t)
    s_t = sI_t - sQ_t # s(t) - GMSK with RF carrier


    return (s_t,s_complex)

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

def gmsk_demod(r_complex,L):
    """
    Function to demodulate a baseband GMSK signal
    Parameters:
        r_complex : received signal at receiver front end (complex form - I+jQ)
        L : oversampling factor
    Returns:
        a_hat : detected binary stream
    """
    I=np.real(r_complex); Q = -np.imag(r_complex); # I,Q streams
    z1 = Q * np.hstack((np.zeros(L), I[0:len(I)-L]))
    z2 = I * np.hstack((np.zeros(L), Q[0:len(I)-L]))
    z = z1 - z2
    a_hat = (z[2*L-1:-L:L] > 0).astype(int) # sampling and hard decision
    #sampling indices depend on the truncation length (k) of Gaussian LPF defined in the modulator
    return a_hat
