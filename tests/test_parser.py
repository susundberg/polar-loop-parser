
import unittest


import Parser



  
class TestParserAdding( unittest.TestCase ):  
  data = [0xde,0x0f,0x10,0x0c,0x18,0x1c,0x12,0x08,0x08,0x08,0x10,0x10,0x18,0x00]
  
  
  def setUp( self ):
    self.parser = Parser.Parser( self.data, None, None )
    
  def test_000(self):
    p0 = self.parser.drop(0)
    p1 = self.parser.drop(1)
    p2 = self.parser.drop(2)
    
    pp0 = p0 + p1
    assert( pp0.parent == self.parser)
    assert( pp0.parent_offset == 0)
    assert( pp0.parent_size == 1)
    
    pp0 = p2 + pp0 
    assert( pp0.parent == self.parser)
    assert( pp0.parent_offset == 0)
    assert( pp0.parent_size == 3)
    
  def test_001(self):
    self.parser.drop(4)
    p1 = self.parser.drop(2)
    p2 = self.parser.drop(2)
    pp0 = p1 + p2
    assert( pp0.parent == self.parser)
    assert( pp0.parent_offset == 4)
    assert( pp0.parent_size == 4)
    
  def test_002(self):
    class TestTag( Parser.Tag ):
      start_tag = [0xde,0x0f]
      stop_tag  = [0x0c,0x18]
      data_len  = 1
      
      def __init__(self, p ):
        p.data = p.data[0]
    
    self.parser.get_tag( TestTag ) 
    self.parser.consume( [0x1c,0x12] )
    
    p1 = self.parser.drop(2)
    p2 = self.parser.drop(2)
    pp0 = p2 + p1
    assert( pp0.parent == self.parser)
    assert( pp0.parent_offset == 7)
    assert( pp0.parent_size == 4)
    self.parser.consume( [0x10,0x18,0x00] )
    assert self.parser.done() == True
    
    
  
class TestParser( unittest.TestCase ):
  data = [0xde,0x0f,0x10,0x0c,0x18,0x1c,0x12,0x08,0x08,0x08,0x10,0x10,0x18,0x00]
  
  
  def setUp( self ):
    self.parser = Parser.Parser( self.data, None, None )
  
  def test_200( self ):
    """ Check that we read tag properly """
    class TestTag( Parser.Tag ):
      start_tag = [0xde,0x0f]
      stop_tag  = [0x0c,0x18]
      data_len  = 1
      
      def __init__(self, p ):
        p.data = p.data[0]
        
    self.parser.get_tag( TestTag ) 
    self.parser.consume( [0x1c,0x12] )

  def test_300( self ):
    """ Check that we can drop and add parsers """
    p = self.parser.drop(0)
    assert len(p.data) == 0
    assert self.parser.offset == 0
    p = p + self.parser.drop(1)
    assert self.parser.offset == 1
    p = p + self.parser.drop(1)
    assert self.parser.offset == 2
    assert p.data == [0xde,0x0f]
    
    
    
    
  def test_000(self):
    assert len( self.parser.__repr__() ) > 32 
  
  def test_001( self ):
    """ Test that start tag and len works """
    pp = self.parser.split( [0xde], data_len = 1 )
    assert len(pp.data) == 1
    self.assertRaises( Parser.NotFound, self.parser.split, [0xde], data_len = 1 )
 
    pp = self.parser.split( [0x10,0x0c], data_len = 4 )
    assert len(pp.data) == 4
 
  def test_002_00( self ):
    """ Test that start - stop tag works """
    pp = self.parser.split( [0xde], stop_tag = [0x00] )
    assert len(pp.data) == len(self.data) - 2

  def test_002_01( self ):
    """ Test that start - stop tag works """
    
    pp = self.parser.split( [0xde,0x0f,0x10], stop_tag = [0x10,0x18,0x00] )
    assert len(pp.data) == len(self.data) - 6
    
  def test_002_02( self ):
    """ Test that start - stop tag works """
    self.assertRaises( Parser.NotFound, self.parser.split, [0xde,0x0f,0x10], stop_tag = [0xff,0xff] )
    self.parser.max_seek = 2
    self.assertRaises( Parser.NotFound, self.parser.split, [0xde,0x0f,0x10], stop_tag = [0xff] )
    
    self.parser.max_seek = 32
    
    # Check that we are still at
    pp1 = self.parser.split( [0xde,0x0f], stop_tag = [0x0c, 0x18] )
    assert len(pp1.data) == 1
    pp2 = self.parser.split( [0x1c,0x12], stop_tag = [0x10] )
    assert len(pp2.data) == 3
    
    
  def test_003( self ):  
    """ Check that stop_tag and data len works """
    self.assertRaises( Parser.UnknownData, self.parser.split, [0xde,0x0f,0x10], data_len = 5, stop_tag = [0x00] )
    self.parser.split ( [0xde,0x0f,0x10], data_len = len(self.data) - 4, stop_tag = [0x00] )
  
  def test_004( self ):  
    """ Check that all is done works """
    assert self.parser.done() == False
    pp = self.parser.split( [0xde], stop_tag = [0x00] )
    assert self.parser.done() == True
    
    
  def test_100( self ):  
    """ Check consume works """
    self.parser.consume( [0xde,0x0f,0x10,0x0c,0x18] )
    self.parser.consume( [0x1c,0x12,0x08,0x08,0x08,0x10,0x10,0x18,0x00] )
    assert self.parser.done() == True
      
  def test_101( self ):  
    """ Check consume works """
    self.assertRaises( Parser.NotFound, self.parser.consume, [0xff,0xff,0x10,0x0c,0x18] )

  def test_110( self ):  
    """ Check consume works """
    pp = self.parser.drop( 5 )
    assert len(pp.data) == 5
    
    pp = self.parser.drop( 2 )
    assert pp.data == [0x1c,0x12]
    
    self.parser.consume( [0x08,0x08,0x08,0x10,0x10,0x18,0x00] )
    assert self.parser.done() == True
  
  def test_200( self ):
    """ Check that dynamic split works """
    
    def mock_len( data ):
      left = [0x10,0x0c,0x18,0x1c,0x12,0x08,0x08,0x08,0x10,0x10,0x18,0x00]
      assert (data == left )
      return len(left) - 1
    
    pp = self.parser.split_dynamic( [0xde,0x0f], mock_len )
    assert len(pp.data) == len(self.data)-3
    
  def test_201( self ):
    """ Check that dynamic split does not consume if not found"""
    
    def mock_len( data ):
      raise Parser.NotFound
    
    self.assertRaises( Parser.NotFound, self.parser.split_dynamic, [0xde,0x0f], mock_len  )
    
    assert len(self.parser.data) == len(self.data)
    
    
if __name__ == '__main__':
    unittest.main()