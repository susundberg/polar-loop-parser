# polar-loop-parser
Polar loop binary file parser

This project is stalled and not functional. 

The idea was to make python parsers for the binary files produced by the activity tracker Polar loop.

I did contact Polar customer service (twice) to ask for the format but they never provided such. So i decided to take a reverese-engineering look.

The binary files can be downloaded at least from rooted android devices with normal file expolorer. I did also some bluetooth sniffing, and the traffic seems to be un-encrypted, so it should be doable to directly to communicate with the device.

The binary files then again seems to have some non-standard format, that is quite complex (why o, why!). The data is surely un-encrypted, and you can see the patterns matching to the visualization provided from the polar software.

The project got stalled since lack of time -- i decided to buy pebble -- its better match for my needs. 

You can run the tests in the 'test' directory with:
    python -m unittest --failfast  tests.test_parser

You can try to parse a datafile (see examples) :
   python analyze.py examples/sleeping.bin 


What works (with files SAMPL0*.BPB):
  * Timestamp detection
  * Idle detection
  * Most part of the motion detection

What does not:
  * Interpret the motion tags, what does B125 mean ? 

