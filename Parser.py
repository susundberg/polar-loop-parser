

class NotFound(Exception):
  pass

class UnknownData(Exception):
  pass


def hexstr( data ):
  return ",".join( [ "0x%02x" % d for d in data ] )  

class Tag(object):
  def __init__(self, start_tag, stop_tag, data_len ):
    self.start_tag = start_tag
    self.stop_tag = stop_tag
    self.data_len = data_len
    
  
class Parser(object):
   short = "X"
   
   def __init__(self, data, parent, size ):
     self.data = data
     self.offset = 0
     self.max_seek = 256
     
     if parent == None:
       self.parent        = None
     else:
       self.parent = parent
       self.parent_offset = parent.offset
       self.parent_size   = size
       self.parent.offset += size
   
   
   def __repr__(self):
     return "Parser [" + hexstr(self.data[0:32]) +"] .. tlen %d " % len(self.data)
   
   def __add__(self, other):
     if type(other) != type(self):
       raise TypeError("Custom add not handling that class")
     assert other.offset == 0 
     
     if self.parent is other.parent:
       parent = self.parent 
         
     parser = Parser( self.data + other.data, parent, 0 )
     
     if self.parent_offset == other.parent_offset:
       if self.parent_size == 0:
          before = self
          after  = other
       else:
          before = other
          after  = self
     elif self.parent_offset < other.parent_offset:
       before = self
       after  = other
     else:
       before = other
       after  = self
       
     if before.parent_offset + before.parent_size == after.parent_offset:
       parser.parent_offset = before.parent_offset
       parser.parent_size   = before.parent_size + after.parent_size
     else: # Non continuos area, dont know what to do.
       assert 0, "Non continous area?!"
       
     return parser
       
     
     
   def done( self ):
     return self.offset == len(self.data)
   
   def current( self, show_samples=128 ):
     return Parser( self.data[ self.offset: self.offset+show_samples], self,  0 )
   
   def consume( self, data ):
     if self.data[ self.offset : self.offset + len(data) ] == data:
       self.offset += len(data)
       return
     raise NotFound()
   
   def drop( self, data_len ):
     return Parser( self.data[ self.offset : self.offset + data_len], self, data_len )
   
   def endswith( self, data ):
     self._check_start_tag( data )
     
     if self.offset + len(data) != len(self.data):
       raise NotFound
     return Parser( self.data[self.offset:self.offset + len(data)], self, len(data) )
     
   def get_tag( self, tag_class ):
      if hasattr( tag_class, 'calculate_len' ):
        parser = self.split_dynamic( tag_class.start_tag, tag_class.calculate_len  )
      else :
         parser =  self.split( tag_class.start_tag, stop_tag = tag_class.stop_tag, data_len = tag_class.data_len )
      return tag_class( parser )
   
   def split_dynamic( self, start_tag, calc_len ):
      self._check_start_tag( start_tag )
      data_eaten  = len(start_tag) 
      data = self.data[ self.offset + len(start_tag) : ]
      
      # Can raise NotFound , and thats ok
      data_len = calc_len( data )
      return Parser( data[0:data_len], self, data_eaten + data_len )
    
   
   def _check_start_tag( self, start_tag ):
      if self.data[ self.offset: self.offset + len(start_tag) ] != start_tag:
         raise NotFound()
       
   def compare_to(self, other ):
     my_curr = self.current ()
     other_curr = other.current ()
     print my_curr
     clen = min( len( my_curr.data ), len(other_curr.data) )
     strdesc= ""
     for loop in range(clen):
        strdesc += "%02x" % my_curr.data[loop]
     print strdesc
     strdesc= ""
     for loop in range(clen):
       if my_curr.data[loop] != other_curr.data[loop]:
          strdesc += "%02x" % other_curr.data[loop]
       else:
          strdesc+= ".."
     print strdesc
     
   def split( self, start_tag, stop_tag = None, data_len = 0 ):
      """ Check for starttag from the data. 
          Parameter:
            stop_tag -- if defined, then return data until that
            len -- target length of data between start_tag, stop_tag
          Returns:
            the tag we found between the tags
      """
      self._check_start_tag( start_tag )
      # Raise Notfound if tag is not found
      data_eaten  = len(start_tag) 
      data = self.data[ self.offset + len(start_tag) : ]
      
      if stop_tag is None and data_len > 0 :
        return Parser( data[0:data_len], self, data_eaten + data_len )
      
      assert stop_tag is not None
      
      # Stop tag defined, we must look for it.
      to_seek = min( len(data) - (len(stop_tag) - 1), self.max_seek )
      for loop in range( to_seek ):
        # print data[loop:loop + len(stop_tag)]
        if data[loop:loop + len(stop_tag)] == stop_tag:
          ret_data = data[0:loop]
          break
      else:
         raise NotFound()
       
          
      if data_len > 0 and data_len != len(ret_data):
        raise UnknownData("Tag data length differ from predefined %d vs %d " % ( data_len, len(ret_data) ))
      
      return Parser( ret_data, self,  data_eaten + len(ret_data) + len(stop_tag) )


  
      
    