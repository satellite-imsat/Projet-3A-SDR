"""
Module: DigiCommPy.channels.py
"""
from numpy import sum,isrealobj,sqrt
from numpy.random import standard_normal
import numpy as np

def gaussianLPF(BT, Tb, L, k):
    """
    Generate filter coefficients of Gaussian low pass filter (used in gmsk_mod)
    Parameters:
        BT : BT product - Bandwidth x bit period
        Tb : bit period
        L : oversampling factor (number of samples per bit)
        k : span length of the pulse (bit interval)        
    Returns:
        h_norm : normalized filter coefficients of Gaussian LPF
    """
    B = BT/Tb # bandwidth of the filter
    # truncated time limits for the filter
    t = np.arange(start = -k*Tb, stop = k*Tb + Tb/L, step = Tb/L)
    h = B*np.sqrt(2*np.pi/(np.log(2)))*np.exp(-2 * (t*np.pi*B)**2 /(np.log(2)))
    h_norm=h/np.sum(h)
    return h_norm

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
    c_t = upfirdn(h=[1]*L, x=2*a-1, up = L) #NRZ pulse train c(t)
    
    k=1 # truncation length for Gaussian LPF
    h_t = gaussianLPF(BT,Tb,L,k) # Gaussian LPF with BT=0.25
    b_t = np.convolve(h_t,c_t,'full') # convolve c(t) with Gaussian LPF to get b(t)
    bnorm_t = b_t/max(abs(b_t)) # normalize the output of Gaussian LPF to +/-1
    
    h = 0.5;
    # integrate to get phase information
    phi_t = lfilter(b = [1], a = [1,-1], x = bnorm_t*Ts) * h*np.pi/Tb 
    
    I = np.cos(phi_t)
    Q = np.sin(phi_t) # cross-correlated baseband I/Q signals
    
    s_complex = I - 1j*Q # complex baseband representation
    t = Ts* np.arange(start = 0, stop = len(I)) # time base for RF carrier
    sI_t = I*np.cos(2*np.pi*fc*t); sQ_t = Q*np.sin(2*np.pi*fc*t)
    s_t = sI_t - sQ_t # s(t) - GMSK with RF carrier
    
    if enable_plot:
        fig, axs = plt.subplots(2, 4)
        axs[0,0].plot(np.arange(0,len(c_t))*Ts,c_t);
        axs[0,0].set_title('c(t)');axs[0,0].set_xlim(0,40*Tb)
        axs[0,1].plot(np.arange(-k*Tb,k*Tb+Ts,Ts),h_t);
        axs[0,1].set_title('$h(t): BT_b$='+str(BT))
        axs[0,2].plot(t,I,'--');axs[0,2].plot(t,sI_t,'r');
        axs[0,2].set_title('$I(t)cos(2 \pi f_c t)$');axs[0,2].set_xlim(0,10*Tb)
        axs[0,3].plot(t,Q,'--');axs[0,3].plot(t,sQ_t,'r');
        axs[0,3].set_title('$Q(t)sin(2 \pi f_c t)$');axs[0,3].set_xlim(0,10*Tb)
        axs[1,0].plot( np.arange(0,len(bnorm_t))*Ts,bnorm_t);
        axs[1,0].set_title('b(t)');axs[1,0].set_xlim(0,40*Tb)
        axs[1,1].plot(np.arange(0,len(phi_t))*Ts, phi_t);
        axs[1,1].set_title('$\phi(t)$')
        axs[1,2].plot(t,s_t);axs[1,2].set_title('s(t)');
        axs[1,2].set_xlim(0,20*Tb)
        axs[1,3].plot(I,Q);axs[1,3].set_title('constellation')
        fig.show()        
    return (s_t,s_complex)

def awgn(s,SNRdB,L=1):
    """
    AWGN channel
    
    Add AWGN noise to input signal. The function adds AWGN noise vector to signal
    's' to generate a resulting signal vector 'r' of specified SNR in dB. It also
    returns the noise vector 'n' that is added to the signal 's' and the power
    spectral density N0 of noise added
    
    Parameters:
        s : input/transmitted signal vector
        SNRdB : desired signal to noise ratio (expressed in dB)
            for the received signal
        L : oversampling factor (applicable for waveform simulation)
            default L = 1.
    Returns:
        r : received signal vector (r=s+n)
    """
    gamma = 10**(SNRdB/10) #SNR to linear scale
    
    

    if s.ndim==1:# if s is single dimensional vector
        P=L*sum(abs(s)**2)/len(s) #Actual power in the vector
    else: # multi-dimensional signals like MFSK
        P=L*sum(sum(abs(s)**2))/len(s) # if s is a matrix [MxN]

    N0=P/gamma # Find the noise spectral density    
    print(N0)
    if isrealobj(s):# check if input is real/complex object type
        n = sqrt(N0/2)*standard_normal(s.shape) # computed noise
    else:
        n = sqrt(N0/2)*(standard_normal(s.shape)+1j*standard_normal(s.shape))
    r = s + n # received signal    
    return r


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


N= 100000 # Number of symbols to transmit

fc = 800 # Carrier frequency in Hz (must be < fs/2 and > fg)
L = 16 # oversampling factor
snr = 10

a = np.random.randint(2, size=N) # uniform random symbols from 0's and 1's
(s, s_complex) = gmsk_mod(a,fc,L,0.3) # GMSK modulation


r_complex = awgn(s_complex, snr)

a_hat_hat = gmsk_demod(r_complex, L)

ber_ = np.sum(a !=a_hat_hat)/N # Bit Error Rate Computation
    
print("BER", ber_)

N=100000 # Number of symbols to transmit
EbN0dB = 10
BTs = [0.3] # Gaussian LPF's BT products
fc = 800 # Carrier frequency in Hz (must be < fs/2 and > fg)
L = 16 # oversampling factor


a = np.random.randint(2, size=N) # uniform random symbols from 0's and 1's
(s_t,s_complex) = gmsk_mod(a,fc,L,0.3) # GMSK modulation

r_complex = awgn(s_complex,EbN0dB) # refer Chapter section 4.1
a_hat = gmsk_demod(r_complex,L) # Baseband GMSK demodulation
ber = np.sum(a!=a_hat)/N # Bit Error Rate Computation
print('BER', ber)