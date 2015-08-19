import unittest
import Polar
import analyze



  
class TestParserAdding( unittest.TestCase ):  
  
  def test_000(self):
    

    data = [ int,"foo",int,"foo",bool,int,float ]
    states_before =  {}
    states_after  = {}
    
    analyze.build_state_machine( data, states_before,states_after )
    analyze.finish_building(states_before, states_after )
    