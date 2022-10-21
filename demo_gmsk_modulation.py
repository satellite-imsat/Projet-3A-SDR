# Author : Thomas Aussaguès
# Date : 20 / 10 / 2022
# Contatct : thomas.aussagues@imt-atlantique.net


from functions.gen_signal import random_binary_signal, word_nrz_signal, binary_to_nrz_signal
from functions.mod_gmsk import mod_signal_gmsk, demod_gmsk
import matplotlib.pyplot as plt
import numpy as np
from functions.str2bit import nameFromSignal
from functions.metrics import compute_ber
import matplotlib.pyplot as plt
from functions.mod_gmsk import gmsk_demod
plt.style.use(['science','grid'])

'''
The purpose of this script is to illustrate the GMSK modulation and demodulation of a random (or not) signal.
The performance is evaluated through the binary error rate.

Some general notations :
-> A constant value variable begins with a c
-> A vector variables begins with a v
'''

### We fix the random seed for reproductibility
np.random.seed(1)

### We define some general parameters of the transmitted signal.###
# Each parameter name is followed by the corresponding unit.

# Number of symbols (integer, greater than 0)
c_n_symb = 100000
# Upsampling factor  (integer, greater than 2)
c_up_sampling = 16
# Carrier frequency (in Hertz)
c_fc_hz = 800
# Time-bandwidth product (float, 0.3 for GMSK)
c_time_bandwidth_product = 0.3
# Bitrate used in AIS communcations (float)
c_bit_rate_bit_per_sec = 9600
# Signal-to-Noise-Ratio in dB (float)
c_snr_db = 20

### Signal generation ###
#v_signal = random_binary_signal(n_symb = c_n_symb)

word_dark_vador = '''Don’t be too proud of this technological terror you’ve constructed. The ability to destroy a planet is insignificant next to the power of the Force''' 
word_galadriel = '''
The world is changed. I feel it in the water. I feel it in the earth. I smell it in the air. Much that once was is lost, for none now live who remember it. 
It began with the forging of the Great Rings. Three were given to the Elves, immortal, wisest and fairest of all beings. Seven to the Dwarf-Lords, great miners 
and craftsmen of the mountain halls. And nine, nine rings were gifted to the race of Men, who above all else desire power. For within these rings was bound the 
strength and the will to govern each race. But they were all of them deceived, for another ring was made. Deep in the land of Mordor, in the Fires of Mount Doom, 
the Dark Lord Sauron forged a master ring, and into this ring he poured his cruelty, his malice and his will to dominate all life. One ring to rule them all. One by one, 
the free lands of Middle-Earth fell to the power of the Ring, but there were some who resisted. A last alliance of men and elves marched against the armies of Mordor, and on 
the very slopes of Mount Doom, they fought for the freedom of Middle-Earth. Victory was near, but the power of the ring could not be undone. It was in this moment, when all hope had faded, 
that Isildur, son of the king, took up his father's sword. Sauron, enemy of the free peoples of Middle-Earth, was defeated. 
The Ring passed to Isildur, who had this one chance to destroy evil forever, but the hearts of men are easily corrupted. And the ring of power has a will of its own. 
It betrayed Isildur, to his death. And some things that should not have been forgotten were lost. History became legend. Legend became myth. 
And for two and a half thousand years, the ring passed out of all knowledge. Until, when chance came, it ensnared another bearer. It came to the creature Gollum, who took 
it deep into the tunnels of the Misty Mountains. And there it consumed him. The ring gave to Gollum unnatural long life. For five hundred years it poisoned his mind, 
and in the gloom of Gollum's cave, it waited. Darkness crept back into the forests of the world. Rumor grew of a shadow in the East, whispers of a nameless fear, 
and the Ring of Power perceived its time had come. It abandoned Gollum, but then something happened that the Ring did not intend. 
It was picked up by the most unlikely creature imaginable: a hobbit, Bilbo Baggins, of the Shire.
For the time will soon come when hobbits will shape the fortunes of all.
'''
word_oss_117 = '''23 à 0 ! C'est la piquette Jack ! Tu sais pas jouer Jack ! T'es mauvais !'''

word = word_oss_117

v_signal = word_nrz_signal(word_galadriel)

plt.figure('binary_signal')
v_time = np.arange(start = 0, stop = v_signal.shape[0], step = 1) * 1 / c_bit_rate_bit_per_sec
plt.stem(v_time * 1e3, v_signal)
plt.xlim([0, 1 / c_bit_rate_bit_per_sec * 25 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Binary signal')
plt.savefig('figures/binary_signal.pdf', dpi = 300)
plt.close('binary_signal')

plt.figure('nrz_signal')
v_time = np.arange(start = 0, stop = v_signal.shape[0] * c_up_sampling, step = 1) * 1 / (c_bit_rate_bit_per_sec * c_up_sampling)
plt.plot(v_time * 1e3, binary_to_nrz_signal(binary_signal = v_signal, up_sampling_factor = c_up_sampling), marker = '*')
plt.xlim([0, 1 / c_bit_rate_bit_per_sec * 25 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('NRZ signal')
plt.savefig('figures/nrz_signal.pdf', dpi = 300)
plt.close('nrz_signal')

### Signal GMSK modulation
v_signal_gmsk = mod_signal_gmsk(v_signal = v_signal, 
                                fc = c_fc_hz, 
                                up_sampling_factor = c_up_sampling, 
                                time_bandwidth_product = c_time_bandwidth_product)

plt.figure('unoised_modulated_signal')
v_time = np.arange(start = 0, stop = v_signal_gmsk.shape[0], step = 1) * 1 / (c_bit_rate_bit_per_sec * c_up_sampling)
plt.plot(v_time * 1e3, np.real(v_signal_gmsk))
plt.xlim([0, 1 / c_bit_rate_bit_per_sec * 25 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Unoised modulated signal')
plt.savefig('figures/unoised_modulated_signal.pdf', dpi = 300)
plt.close('unoised_modulated_signal')

### Propgation over the chosen channel ###

# Here, we consider a simple AWGN channel with no attenuation

# First we get the signal power defined as the signal squared norm divided by the number of symbols
signal_power = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]
# Then, we compute the noise power (in linear units) by applying the SNR definition in linear units.
noise_power = signal_power / (10 ** (c_snr_db / 10))
# Finally, we simply add a random complex noise to the signal since we have an AWGN channel.
v_signal_gmsk = v_signal_gmsk + np.sqrt(noise_power / 2) * (np.random.randn(v_signal_gmsk.shape[0]) + 1j * np.random.randn(v_signal_gmsk.shape[0]))

### Signal GMSK demodulation ###

v_hat = demod_gmsk(v_signal_gmsk, c_fc_hz, c_up_sampling)
v_hat_hat = gmsk_demod(v_signal_gmsk, c_up_sampling)
### Binary Error Rate 

ber = compute_ber(demodulated_signal =  v_hat, ground_truth_signal = v_signal)



### Printing results
print('\n', '*' * 60)
print(f"\nThe emitted message was : {word}")
print(f"The receveid one is : {nameFromSignal(signal = v_hat)}")
print(f"For a SNR of {c_snr_db} dB, we have a BER of {ber}\n")
print('*' * 60, '\n')