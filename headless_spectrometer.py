#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Thu Jan 18 21:43:36 2018
##################################################

from datetime import datetime
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import numpy as np
import osmosdr
import radio_astro
import time


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.vec_length = vec_length = 4096
        self.sinc_sample_locations = sinc_sample_locations = np.arange(-np.pi*4/2.0, np.pi*4/2.0, np.pi/vec_length)
        self.timenow = timenow = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.sinc = sinc = np.sinc(sinc_sample_locations/np.pi)
        self.prefix = prefix = "/home/kania/radio/data/"
        self.samp_rate = samp_rate = 10e6
        self.recfile = recfile = prefix + timenow + "_Drift.h5"
        self.integration_time = integration_time = 4
        self.freq = freq = 1419e6
        self.display_integration = display_integration = 0.5
        self.custom_window = custom_window = sinc*np.hamming(4*vec_length)

        ##################################################
        # Blocks
        ##################################################
        self.radio_astro_hdf5_sink_1 = radio_astro.hdf5_sink(vec_length, recfile, 'A180E55', freq - samp_rate/2, samp_rate/vec_length, 'amber:39.659,-79.872.  horn3b, lna V3 mod, thin, 5.2/5.2cm probe, 20,12,10')
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'airspy=0,bias=1,pack=0' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(20, 0)
        self.osmosdr_source_0.set_if_gain(12, 0)
        self.osmosdr_source_0.set_bb_gain(10, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.fft_vxx_0 = fft.fft_vcc(vec_length, True, (window.rectangular(vec_length)), True, 1)
        self.blocks_stream_to_vector_0_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_multiply_const_vxx_0_2 = blocks.multiply_const_vcc((custom_window[-vec_length:]))
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vcc((custom_window[2*vec_length:3*vec_length]))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc((custom_window[vec_length:2*vec_length]))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((custom_window[0:vec_length]))
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(vec_length)
        self.blocks_integrate_xx_0_0 = blocks.integrate_ff(int(display_integration*samp_rate/vec_length), vec_length)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(int((integration_time)*samp_rate/vec_length)/int(display_integration*samp_rate/vec_length), vec_length)
        self.blocks_delay_0_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, 3*vec_length)
        self.blocks_delay_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, 2*vec_length)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(vec_length)
        self.blocks_add_xx_0 = blocks.add_vcc(vec_length)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_delay_0_0_0, 0), (self.blocks_stream_to_vector_0_2, 0))
        self.connect((self.blocks_delay_0_0_0_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.radio_astro_hdf5_sink_1, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_2, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vxx_0_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_2, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_delay_0_0_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_delay_0_0_0_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_stream_to_vector_0, 0))

    def get_vec_length(self):
        return self.vec_length

    def set_vec_length(self, vec_length):
        self.vec_length = vec_length
        self.set_custom_window(self.sinc*np.hamming(4*self.vec_length))
        self.set_sinc_sample_locations(np.arange(-np.pi*4/2.0, np.pi*4/2.0, np.pi/self.vec_length))
        self.blocks_multiply_const_vxx_0_2.set_k((self.custom_window[-self.vec_length:]))
        self.blocks_multiply_const_vxx_0_1.set_k((self.custom_window[2*self.vec_length:3*self.vec_length]))
        self.blocks_multiply_const_vxx_0_0.set_k((self.custom_window[self.vec_length:2*self.vec_length]))
        self.blocks_multiply_const_vxx_0.set_k((self.custom_window[0:self.vec_length]))
        self.blocks_delay_0_0_0_0.set_dly(3*self.vec_length)
        self.blocks_delay_0_0_0.set_dly(2*self.vec_length)
        self.blocks_delay_0_0.set_dly(self.vec_length)

    def get_sinc_sample_locations(self):
        return self.sinc_sample_locations

    def set_sinc_sample_locations(self, sinc_sample_locations):
        self.sinc_sample_locations = sinc_sample_locations
        self.set_sinc(np.sinc(self.sinc_sample_locations/np.pi))

    def get_timenow(self):
        return self.timenow

    def set_timenow(self, timenow):
        self.timenow = timenow
        self.set_recfile(self.prefix + self.timenow + "_Drift.h5")

    def get_sinc(self):
        return self.sinc

    def set_sinc(self, sinc):
        self.sinc = sinc
        self.set_custom_window(self.sinc*np.hamming(4*self.vec_length))
        self.set_sinc(np.sinc(self.sinc_sample_locations/np.pi))

    def get_prefix(self):
        return self.prefix

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.set_recfile(self.prefix + self.timenow + "_Drift.h5")

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_recfile(self):
        return self.recfile

    def set_recfile(self, recfile):
        self.recfile = recfile

    def get_integration_time(self):
        return self.integration_time

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)

    def get_display_integration(self):
        return self.display_integration

    def set_display_integration(self, display_integration):
        self.display_integration = display_integration

    def get_custom_window(self):
        return self.custom_window

    def set_custom_window(self, custom_window):
        self.custom_window = custom_window
        self.blocks_multiply_const_vxx_0_2.set_k((self.custom_window[-self.vec_length:]))
        self.blocks_multiply_const_vxx_0_1.set_k((self.custom_window[2*self.vec_length:3*self.vec_length]))
        self.blocks_multiply_const_vxx_0_0.set_k((self.custom_window[self.vec_length:2*self.vec_length]))
        self.blocks_multiply_const_vxx_0.set_k((self.custom_window[0:self.vec_length]))


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.start()
    #try:
    #    raw_input('Press Enter to quit: ')
    #except EOFError:
    #    pass
    time.sleep(300)
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
