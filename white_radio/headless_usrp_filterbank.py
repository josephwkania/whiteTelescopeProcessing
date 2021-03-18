#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Headless Usrp Filterbank
# GNU Radio version: 3.8.2.0

from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time


class headless_usrp_filterbank(gr.top_block):

    def __init__(self, fast_integration=0.0005, freq=1.4205e9, samp_rate=25e6, vec_length=256):
        gr.top_block.__init__(self, "Headless Usrp Filterbank")

        ##################################################
        # Parameters
        ##################################################
        self.fast_integration = fast_integration
        self.freq = freq
        self.samp_rate = samp_rate
        self.vec_length = vec_length

        ##################################################
        # Variables
        ##################################################
        self.integration_time = integration_time = 10

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_1 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                otw_format="sc8",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_1.set_samp_rate(samp_rate)
        self.uhd_usrp_source_1.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_1.set_center_freq(freq, 0)
        self.uhd_usrp_source_1.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_1.set_gain(35, 0)
        self.uhd_usrp_source_1.set_auto_dc_offset(True, 0)
        self.uhd_usrp_source_1.set_auto_iq_balance(True, 0)
        self.uhd_usrp_source_1.set_min_output_buffer(8192)
        self.uhd_usrp_source_1.set_max_output_buffer(16384)
        self.fft_vxx_0 = fft.fft_vcc(vec_length, True, window.rectangular(vec_length), True, 4)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec_length)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(vec_length)
        self.blocks_integrate_xx_0_0 = blocks.integrate_ff(int(fast_integration*samp_rate/vec_length), vec_length)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*vec_length, 'test.bin', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(vec_length)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.blocks_integrate_xx_0_0, 0))
        self.connect((self.blocks_integrate_xx_0_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.blocks_stream_to_vector_0, 0))


    def get_fast_integration(self):
        return self.fast_integration

    def set_fast_integration(self, fast_integration):
        self.fast_integration = fast_integration

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_1.set_center_freq(self.freq, 0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_1.set_samp_rate(self.samp_rate)

    def get_vec_length(self):
        return self.vec_length

    def set_vec_length(self, vec_length):
        self.vec_length = vec_length

    def get_integration_time(self):
        return self.integration_time

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time




def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--fast-integration", dest="fast_integration", type=eng_float, default="500.0u",
        help="Set fast_integration [default=%(default)r]")
    parser.add_argument(
        "--freq", dest="freq", type=eng_float, default="1.4205G",
        help="Set freq [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=eng_float, default="25.0M",
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--vec-length", dest="vec_length", type=intx, default=256,
        help="Set vec_length [default=%(default)r]")
    return parser


def main(top_block_cls=headless_usrp_filterbank, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(fast_integration=options.fast_integration, freq=options.freq, samp_rate=options.samp_rate, vec_length=options.vec_length)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
