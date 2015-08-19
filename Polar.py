
import Parser

# HEADER = HEADER[:114]0xdf,0x0f,0x10,0x01,0x18





class TagDate( Parser.Tag ) :
  # STA 0x17,0x0a,0x07,0x08,
  # DAA 0xdf,0x0f,0x10,0x01,0x18,0x10,
  # END 0x12,0x08,0x08
  start_tag = [0x17,0x0a,0x07]
  stop_tag  = [0x12,0x08,0x08]
  data_len  = 7
  short     = "D"
  
  def __init__( self, parser ):
    self.year = 1792 + parser.split( [0x08], data_len=1, stop_tag = [0x0f] ).data[0] 
    self.month = parser.split( [0x10], data_len=1  ).data[0]
    self.day = parser.split( [0x18], data_len=1  ).data[0]
    assert parser.done() == True
  
  def __repr__(self):
    return super( TagDate, self).__repr__() + " : " + str( (self.year, self.month, self.day ) ) 
  
  
  def __eq__(self, other ):
    if type(other) != type(self):
      raise TypeError()
    
    return all( ( other.year == self.year, other.month == self.month, other.day == self.day ) )


class TagDateTime(Parser.Tag):
  start_tag = [0x3a,0x20,0x08]
  stop_tag  = [0x00,0x00,0x80]
  data_len  = 0
  
  @property
  def short(self):
    return "\nT%02d%02d%02d" % (self.time[0] ,self.time[1],self.time[2]  )
  
  def __init__(self, parser ):
     self.data_head = parser.drop(1).data
     parser.consume([0x12])
     try:
       self.date      = parser.get_tag( TagDate )
     except Parser.NotFound:
       raise Exception("Invalid data : " + str(parser) + " to datetime tag" )
     
     self.time = [ 0,0,0 ]
     self.time[0] = parser.drop(1).data[0]
     parser.consume( [0x10] )
     self.time[1] = parser.drop(1).data[0]
     parser.consume( [0x18] )
     self.time[2] = parser.drop(1).data[0]
     parser.consume( [0x20,0x00,0x18,0x00,0x20,0x78,0x1d] )
                    
     

  def __repr__(self):
    body_str = ",".join( [ "%d" % x for x in self.time ] )
                          
    return super( TagDateTime, self).__repr__() + " : DATE " + str( self.date ) + " HEAD: " + Parser.hexstr(self.data_head) + " BODY: " + body_str
  
  

class TagSample( Parser.Tag ):
  stop_tag  = None
  data_len  = 3
  def __init__(self,  parser ):
    parser.consume([0x00,0x00])
    self.data = parser.drop(1).data[0]
  
  @property
  def short(self):
    ret_str =  "%s(%02x)" % (self.htype, self.data )
    if ret_str == "B(60)" or ret_str == "C(60)" or ret_str == "b(60)":
      return "z"
    return ret_str
  
  def __repr__(self):
    return super( TagSample, self).__repr__() + " : %02x"  % self.data
  
class TagSample0( TagSample ):
  htype = "A"
  color = "bx"
  start_tag = [ 0x40, 0x25 ]
  
class TagSample1( TagSample ):
  htype = "B"
  color = "rx"
  start_tag = [ 0x3f, 0x25 ]

class TagSample2( TagSample ):
  htype = "b"
  color = "gx"
  start_tag = [ 0x00, 0x25 ]

class TagSample3( TagSample ):
  htype = "D"
  color = "mx"
  start_tag = [ 0x41,0x25 ]

  
class TagSampleDelimBase( Parser.Tag ):
  short = "."
  @staticmethod
  def calculate_len( data ):
    dlen = data[0] 
    if  dlen == 0 :
      raise Parser.NotFound
    #if data[dlen] != 0x00:
    #  raise Parser.NotFound    
    return dlen  
    
  def __init__(self, parser ):
    self.data = parser.data
    #parser.parent.data[ parser.parent.offset ] = 0x3f

  def __repr__(self):
    return super( TagSampleDelimBase, self).__repr__() + " : " + Parser.hexstr( self.data )
    
class TagSampleDelim1( TagSampleDelimBase ):  
  start_tag = [0x3f,0x2a]
  
class TagSampleDelim2( TagSampleDelimBase ):  
  start_tag = [0x40,0x2a]


class TagDelimToDate( Parser.Tag ):
  short = "."
  start_tag = [0x00,0x42]
  stop_tag  = [0x19,0x0a]
  data_len  = 0
  def __init__( self, parser ):
    pass
  
class TagNextWillBeDatetime( Parser.Tag ):
    start_tag = [ 0x40,0x2a,0x0f ]
    data_len  = 15
    stop_tag  = None
    short = ","
    def __init__(self,  parser ):
      self.data = parser.data
  
    def __repr__(self):
      return super( TagNextWillBeDatetime, self).__repr__() + " : " + Parser.hexstr(self.data)


  
  
class TagPadding( Parser.Tag ):
  short = "_"
  def __init__( self, parser ):
    self.data = parser.data
    
  def __repr__(self):
    return super( TagPadding, self).__repr__() + " : " + Parser.hexstr(self.data)

class TagPadding3F( TagPadding ):
    type_before = TagDateTime
    type_after  = TagDateTime
    data_is     = [ 0x3f ]
    
class TagPaddingDelimToDate( TagPadding ):
    short = ";"
    type_before = TagSampleDelimBase
    type_after  = TagDateTime
    data_len    = 1

class TagPaddingAfterDate1( TagPadding ):
    type_before = TagDate
    type_after  = None
    data_len    = 15
    
class TagPaddingAfterDate2( TagPadding ):
    type_before = TagDate
    type_after  = TagDateTime
    data_len    = 11

class TagPaddingAtStart(  TagPadding ):
  type_before = TagSample
  type_after  = TagSample
  data_is     = [0x3f,0x2a]
  



class Polar(Parser.Parser):
  
  def __init__(self, data ):
    super(Polar, self ).__init__( data, None, None )
    
  def read_header(self):
    
    self.consume( [0x0a] )
    self.date = self.get_tag( TagDate )
    
    after_date = [0x00,0x10,0x00,0x18,0x00,0x20,0x00,0x18,0x00,0x20,0x78]
    self.consume( after_date )
    self.consume( [0x12,0x08,0x08,0x00,0x10,0x00,0x18,0x1e,0x20,0x00,0x1a,0x08,0x08,0x00,0x10,0x01,0x18,0x00,0x20,0x00,0x32,0x1e,0x0d,0x00,0x00,0x80,0x3f,0x12] )
    assert self.date == self.get_tag( TagDate )
    
    self.consume( after_date )
    for const_chunk in [ [0x3a,0x20,0x08,0x08,0x12] , [0x3a,0x20,0x08,0x02,0x12] , [0x3a,0x20,0x08,0x01,0x12] ]: # Later one seems to hapen at years first day, huh ? 
      try:
        self.consume( const_chunk  )
        break;
      except Parser.NotFound:
        continue
    else:
      import pdb; pdb.set_trace()
      raise Exception("Const chunk not found" )
    
    assert self.date == self.get_tag( TagDate )
    self.consume( after_date )
    #import pdb; pdb.set_trace() # ,0x3f,0x25,0x00,0x00,0x60,0x3f,0x2a,0x00,0x25,0x00,0x00,0x60
    self.consume( [0x1d,0x00,0x00,0x80] )
  
  
  def find_next_tag( self ):
    tag_classes = [ TagSample0, TagSample1, TagSample2, TagSample3, TagSampleDelim1, TagSampleDelim2,TagDate, TagDateTime, TagNextWillBeDatetime, TagDelimToDate ]
    offset_before = self.offset
    for tag_class in tag_classes :
      try:
         tag = self.get_tag( tag_class )
      except Parser.NotFound:
        if ( offset_before != self.offset):
           raise Exception("Invalid class behaviour with %s" % tag_class )
        continue
      return tag
    raise Parser.NotFound()

  
  
  def post_process( self ):
    for loop,sample in enumerate(self.samples):
      if type(sample) != Parser.Parser:
        continue
      
      for pad_class in [TagPadding3F,TagPaddingDelimToDate,TagPaddingAfterDate1 , TagPaddingAfterDate2, TagPaddingAtStart ]:
        if hasattr(pad_class,'data_is') and sample.data != pad_class.data_is:
          continue
        
        if hasattr(pad_class,'data_len') and len(sample.data) != pad_class.data_len:
          continue
        
        if not isinstance( self.samples[loop-1], pad_class.type_before ):
          continue
        
        if pad_class.type_after and loop + 1 < len(self.samples):
          if (not isinstance( self.samples[loop+1], pad_class.type_after )):
            continue
        
        if loop not in self.problems:
          raise Exception("Padding match to %s, original class %s" % ( pad_class, sample ))
                          
        self.samples[loop] = pad_class( sample )
        self.problems.remove( loop )
                
          
    
  def process( self ):
    self.samples = []
    self.problems = []
    while self.done() == False:
      tag = self.process_loop( )
      if tag is None:
        tag = self.consume_until_tag()
      if tag is not None:  
         self.samples.append(tag)
    self.post_process()
    
  def process_loop( self):
    try:
       return self.find_next_tag()
    except Parser.NotFound:
       pass
    return None
  
  def consume_until_tag( self ):
    # No valid tag found, drop data
    const_chunk = self.drop(0)
    tag = None
    while self.done() == False:
      try:
        tag = self.find_next_tag()
      except Parser.NotFound:
        const_chunk = const_chunk + self.drop(1)
        continue
      break
    
    self.samples.append( const_chunk )
    self.problems.append( len(self.samples) - 1 )
    return tag
    

