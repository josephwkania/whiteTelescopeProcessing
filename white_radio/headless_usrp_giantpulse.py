#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Headless Usrp Giantpulse
# GNU Radio version: 3.7.13.5
##################################################

from datetime import datetime
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import numpy as np
import radio_astro
import time


class headless_usrp_giantpulse(gr.top_block):

    def __init__(self, decimation_factor=4, fast_integration=0.0005, freq=1.4205e9, giant_prefix="/home/dspradio/giantPulses/", prefix="/home/dspradio/grc_data/", samp_rate=2.5e6, vec_length=1024):
        gr.top_block.__init__(self, "Headless Usrp Giantpulse")

        ##################################################
        # Parameters
        ##################################################
        self.decimation_factor = decimation_factor
        self.fast_integration = fast_integration
        self.freq = freq
        self.giant_prefix = giant_prefix
        self.prefix = prefix
        self.samp_rate = samp_rate
        self.vec_length = vec_length

        ##################################################
        # Variables
        ##################################################
        self.sinc_sample_locations = sinc_sample_locations = np.arange(-np.pi*4/2.0, np.pi*4/2.0, np.pi/vec_length)
        self.timenow = timenow = datetime.utcnow().strftime("%Y-%m-%d_%H.%M.%S")
        self.sinc = sinc = np.sinc(sinc_sample_locations/np.pi)
        self.timeUTC = timeUTC = datetime.utcnow()
        self.recfile = recfile = prefix + timenow + "_Drift.h5"
        self.integration_time = integration_time = 10
        self.giantout_bin = giantout_bin = giant_prefix + timenow + ".bin"
        self.custom_window = custom_window = sinc*np.hamming(4*vec_length)

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_1 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_1.set_samp_rate(samp_rate)
        self.uhd_usrp_source_1.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)
        self.uhd_usrp_source_1.set_center_freq(freq, 0)
        self.uhd_usrp_source_1.set_gain(35, 0)
        self.uhd_usrp_source_1.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_1.set_auto_dc_offset(True, 0)
        self.uhd_usrp_source_1.set_auto_iq_balance(True, 0)
        self.radio_astro_hdf5_sink_1 = radio_astro.hdf5_sink(float, 1, vec_length, "True", recfile, 'A180E55', freq - samp_rate/2, samp_rate/vec_length, 'amber:39.659,-79.872.  horn3b, lna V3 mod, thin, 5.2/5.2cm probe, 20,12,10')
        self.fft_vxx_0 = fft.fft_vcc(vec_length, True, (window.rectangular(vec_length)), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, vec_length)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_float*1, vec_length/decimation_factor)
        self.blocks_stream_to_vector_0_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_multiply_const_vxx_0_2 = blocks.multiply_const_vcc((custom_window[-vec_length:]))
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vcc((custom_window[2*vec_length:3*vec_length]))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc((custom_window[vec_length:2*vec_length]))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((custom_window[0:vec_length]))
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(vec_length)
        self.blocks_integrate_xx_1 = blocks.integrate_ff(decimation_factor, 1)
        self.blocks_integrate_xx_0_0 = blocks.integrate_ff(int(fast_integration*samp_rate/vec_length), vec_length)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(int((integration_time)*samp_rate/vec_length)/int(fast_integration*samp_rate/vec_length), vec_length)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*vec_length/decimation_factor, giantout_bin, False)
        self.blocks_file_sink_0.set_unbuffered(False)
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
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_integrate_xx_1, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_2, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vxx_0_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_2, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_integrate_xx_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_delay_0_0_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_delay_0_0_0_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_stream_to_vector_0, 0))

    def get_decimation_factor(self):
        return self.decimation_factor

    def set_decimation_factor(self, decimation_factor):
        self.decimation_factor = decimation_factor

    def get_fast_integration(self):
        return self.fast_integration

    def set_fast_integration(self, fast_integration):
        self.fast_integration = fast_integration

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_1.set_center_freq(self.freq, 0)

    def get_giant_prefix(self):
        return self.giant_prefix

    def set_giant_prefix(self, giant_prefix):
        self.giant_prefix = giant_prefix
        self.set_giantout_bin(self.giant_prefix + self.timenow + ".bin")

    def get_prefix(self):
        return self.prefix

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.set_recfile(self.prefix + self.timenow + "_Drift.h5")

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_1.set_samp_rate(self.samp_rate)

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
        self.set_giantout_bin(self.giant_prefix + self.timenow + ".bin")

    def get_sinc(self):
        return self.sinc

    def set_sinc(self, sinc):
        self.sinc = sinc
        self.set_custom_window(self.sinc*np.hamming(4*self.vec_length))
        self.set_sinc(np.sinc(self.sinc_sample_locations/np.pi))

    def get_timeUTC(self):
        return self.timeUTC

    def set_timeUTC(self, timeUTC):
        self.timeUTC = timeUTC

    def get_recfile(self):
        return self.recfile

    def set_recfile(self, recfile):
        self.recfile = recfile

    def get_integration_time(self):
        return self.integration_time

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time

    def get_giantout_bin(self):
        return self.giantout_bin

    def set_giantout_bin(self, giantout_bin):
        self.giantout_bin = giantout_bin
        self.blocks_file_sink_0.open(self.giantout_bin)

    def get_custom_window(self):
        return self.custom_window

    def set_custom_window(self, custom_window):
        self.custom_window = custom_window
        self.blocks_multiply_const_vxx_0_2.set_k((self.custom_window[-self.vec_length:]))
        self.blocks_multiply_const_vxx_0_1.set_k((self.custom_window[2*self.vec_length:3*self.vec_length]))
        self.blocks_multiply_const_vxx_0_0.set_k((self.custom_window[self.vec_length:2*self.vec_length]))
        self.blocks_multiply_const_vxx_0.set_k((self.custom_window[0:self.vec_length]))


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--decimation-factor", dest="decimation_factor", type="intx", default=4,
        help="Set decimation_factor [default=%default]")
    parser.add_option(
        "", "--fast-integration", dest="fast_integration", type="eng_float", default=eng_notation.num_to_str(0.0005),
        help="Set fast_integration [default=%default]")
    parser.add_option(
        "", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(1.4205e9),
        help="Set freq [default=%default]")
    parser.add_option(
        "", "--giant-prefix", dest="giant_prefix", type="string", default="/home/dspradio/giantPulses/",
        help="Set giant_prefix [default=%default]")
    parser.add_option(
        "", "--prefix", dest="prefix", type="string", default="/home/dspradio/grc_data/",
        help="Set prefix [default=%default]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(2.5e6),
        help="Set samp_rate [default=%default]")
    parser.add_option(
        "", "--vec-length", dest="vec_length", type="intx", default=1024,
        help="Set vec_length [default=%default]")
    return parser


def main(top_block_cls=headless_usrp_giantpulse, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(decimation_factor=options.decimation_factor, fast_integration=options.fast_integration, freq=options.freq, giant_prefix=options.giant_prefix, prefix=options.prefix, samp_rate=options.samp_rate, vec_length=options.vec_length)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
