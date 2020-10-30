def main(top_block_cls=headless_airspy, options=None):

    tb = top_block_cls()
    tb.start()
    #try:
    #    raw_input('Press Enter to quit: ')
    #except EOFError:
    #    pass
    time.sleep(300)
    tb.stop()
    tb.wait()
