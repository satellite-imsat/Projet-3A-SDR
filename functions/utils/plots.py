#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   plots.py
@Time    :   2022/12/30 14:32:32
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''

import numpy as np
import matplotlib.pyplot as plt
plt.style.use(['science','grid'])

def plot_correlation_detector_output(v_corr_start : np.array, v_corr_stop : np.array, threshold : float, fs_hz : float, start_pos : int, end_pos : int, title : str, name : str):

    # Compute the time vector
    v_time = np.arange(start = 0, stop = v_corr_start.shape[0], step = 1) * 1 / fs_hz
 
    #
    fig = plt.figure() 
    ax = plt.subplot(111)
    ax.plot(v_time * 1e3, v_corr_start, label = "Corr  start")
    ax.plot(v_time * 1e3, v_corr_stop, label = "Corr. end")
    ax.plot(v_time * 1e3, np.ones_like(v_time) * threshold, label = "Threshold")

    if start_pos is not None : 
        ax.plot([start_pos / fs_hz * 1e3, start_pos / fs_hz * 1e3], [0, np.max(v_corr_start)], label = "Start (g.t.)", linestyle = "--", color = "k") 
    if end_pos is not None :
        ax.plot([end_pos / fs_hz * 1e3, end_pos / fs_hz * 1e3], [0, np.max(v_corr_stop)], label = "End (g.t.)", linestyle = "--", color = "k")
    
    ax.set_xlabel("Lag $\\tau$ (in ms)") 
    ax.set_ylabel("Correlation") 
    ax.set_title(title)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
            fancybox=True, shadow=True, ncol=3)
    plt.savefig("figures/demo_detection/" + name + ".pdf", dpi = 300)