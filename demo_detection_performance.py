from functions.utils.gen_signal import random_binary_signal
import numpy as np
from functions.dsp.detection import correlation_detector

from functions.utils.gen_signal import random_binary_signal
from functions.dsp.modulation import mod_signal_gmsk, differential_decoder
from functions.dsp.channels import awgn_channel
import matplotlib.pyplot as plt
import numpy as np
from functions.utils.metrics import compute_ber
import matplotlib.pyplot as plt
plt.style.use(['science','grid'])


############################# Parameters #############################

# We fix the random seed for reproductibility
#np.random.seed(1)

# General parameters of the transmitted signal.
# Each parameter name is followed by the corresponding unit.

# AIS signal time length (in s)
c_signal_duration_s = 26.66e-3

# AIS ramp-up bits
v_ais_ramp_up = np.zeros(8)

# AIS start flag
v_ais_start_flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])

# AIS preamble
v_ais_preamble = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

# AIS first bits : reference for signal detection
v_ais_ref = np.hstack((v_ais_ramp_up, v_ais_preamble, v_ais_start_flag))

# Bitrate used in AIS communcations (float)
c_bit_rate_bit_per_sec = 9600

# Number of symbols (integer, greater than 0)
c_n_symb = int(c_bit_rate_bit_per_sec * c_signal_duration_s)

# Upsampling factor  (integer, greater than 2) 
# => the sampling frequency is c_bit_rate_bit_per_sec * c_up_sampling
c_up_sampling = 24

# Sampling frequency
c_fs_hz = c_bit_rate_bit_per_sec * c_up_sampling

# Time-bandwidth product (float, 0.4 for AIS)
c_time_bandwidth_product = 0.4

# Desried Signal-to-Noise-Ratio in dB at the RX (float)
c_snr_db = 10

c_threshold = 700


v_preamble_tx = mod_signal_gmsk(v_signal = v_ais_ref, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product)



def generate_data_h1(n_signals, n_symb, fs_hz, up_sampling_factor, time_bandwidth_product, snr_db, v_ais_ref):

    signals_list = list()

    for n in range(n_signals):

        v_signal = random_binary_signal(n_symb = n_symb)
        start_index = np.random.randint(low = 0, high = n_symb - v_ais_ref.shape[0] + 1)
        v_signal[start_index : start_index + v_ais_ref.shape[0]] = v_ais_ref
        v_signal = mod_signal_gmsk(v_signal = v_signal, 
                            fs_hz = fs_hz,
                            up_sampling_factor = up_sampling_factor, 
                            time_bandwidth_product = time_bandwidth_product)
        v_signal = awgn_channel(v_signal = v_signal, snr_db = snr_db)

        signals_list.append(v_signal)

    return signals_list

def generate_data_h0(n_signals, n_symb, fs_hz, up_sampling_factor, time_bandwidth_product, snr_db, v_ais_ref):

    signals_list = list()

    for n in range(n_signals):

        v_signal = np.random.randn(n_symb) + 1j * np.random.randn(n_symb)

        signals_list.append(v_signal)

    return signals_list

size, power = [], []

signals_h1 = generate_data_h1(1000, c_n_symb, c_fs_hz, c_up_sampling, c_time_bandwidth_product, c_snr_db, v_ais_ref)
signals_h0 = generate_data_h0(1000, c_n_symb, c_fs_hz, c_up_sampling, c_time_bandwidth_product, c_snr_db, v_ais_ref)

for t in np.arange(0.4, -0.01, -0.01) :

    power.append(np.mean([correlation_detector(v_signal, v_preamble_tx, t)[0] for v_signal in signals_h1]))
    size.append(np.mean([correlation_detector(v_signal, v_preamble_tx, t)[0] for v_signal in signals_h0]))

print(power, size)
import matplotlib.pyplot as plt

plt.figure()
plt.plot(size, power)
plt.show()