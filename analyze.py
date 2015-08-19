import argparse
import subprocess
import re
import Polar
import Parser

def get_args():
    parser = argparse.ArgumentParser(description='Split file from hex to aligned values')
    parser.add_argument('filename', nargs='+')
    return parser.parse_args()


class Problems:
  
  def __init__(self):
    self.probs = []

  def addfile( self, filename, probs ):
    for prob in probs:
      prob["filename"] = filename
      self.probs.append( prob )

  def filter_data_contains(self, offset, data ):
    ret = []
    for prob in self.probs:
      if prob["data"][offset:offset+len(data)] == data:
        ret.append(prob)
    return ret
  
  def show_problems(self, probs):
    for prob in probs:
      print "%s at 0x%08x (len 0x%08x) : %s" % ( prob["filename"], prob["start"], len(prob["data"]), Header.get_hex(prob["data"]))
      
  def get_split(self, data_prefix, data_postfix ):
    ret = [] 
    for prob in self.probs:
      offset = 0
      try:
        while True:
           p = self.get_split_loop( prob, offset, data_prefix, data_postfix )
           offset += p["offset"] + len(p["data"])
           ret.append(p)
      except NotFound:   
        pass
    return ret

  def get_split_loop( self, prob, offset, data_prefix, data_postfix ):
      data = prob["data"][offset:]
      
      for loop_start in range( len( data ) - len(data_prefix) -len(data_postfix) ):
         if data[loop_start:loop_start + len(data_prefix)] != data_prefix:
           continue
         break
      else:
        raise NotFound
      data = data[ loop_start: ]
      for loop_stop in range( len( data ) - len(data_postfix) ):
         if data[loop_stop:loop_stop + len(data_postfix)] != data_postfix:
           continue
         break
      else:
        raise NotFound
      data = data[ 0:loop_stop + len(data_postfix) ]
      return {'filename' : prob['filename'], 'start' : prob['start'], 'offset' : offset + loop_start,
              'data' : data }

      
def get_problems( filenames):
  probs = Problems()
  for filename in filenames:
      with open(filename, 'rb') as fid:
         data = fid.read()
         data = [ ord(d) for d in data ]
      act = Header.ProcessData( data)
      act.process_data()
      probs.addfile( filename, act.problems )
  return probs    
      #act  = Header.process_data( data )
#      import pdb; pdb.set_trace() 


def dict_problems( polar, numid, problems ):
  problem = polar.samples[numid]
  if len(problem.data)>=2:
     prefix = "%02x,%02x" % (problem.data[0],problem.data[1] )  
  else:
     prefix = "%02x" % problem.data[0]
  if prefix not in problems:
    problems[prefix] = []
  problems[prefix].append( (problem, polar.samples[numid-1], polar.samples[numid+1]) )
    
def build_state_machine( samples, states_before, states_after ):
   build_state_machine_( samples, states_after , +1 )
   build_state_machine_( samples, states_before, -1 )
   
def build_state_machine_( samples, states, direction ):
  
  
  for loop,sample in enumerate(samples):
    
    if loop+direction < 0 or loop+direction >= len(samples):
      continue
    if type(sample ) not in states:
      states[ type(sample) ] = {}
    target = states[ type(sample) ]
    next_type = type( samples[loop + direction ] )
    if  next_type not in target:
      target[ next_type ] = 1
    else:
      target[ next_type ] += 1

def finish_building( states_before, states_after ):
    def normalize( next_states ):
      ret_array = []
      total_nexts = 0
      for k,v in next_states.items():
          total_nexts += v
      for k,v in next_states.items():
        ret_array.append( (next_states[k]/float(total_nexts), next_states[k], k) )
      return sorted(ret_array, key=lambda tup: tup[0]) 
    
    all_types = set()
    for stype in states_before:
      states_before[stype] = normalize( states_before[stype] )
      all_types .add(stype)
    for stype in states_after:
      states_after[stype]  = normalize( states_after[stype] )
      all_types .add(stype)
      
    def print_all( strdesc, tuples ):
      for val,totcount,classname in tuples:
        print "   " + strdesc + "%f %s (total counts %d)" % (val,classname, totcount)
    for stype in sorted(all_types):
        print "CLASS " + str(stype)
        if stype in states_before:
          print_all("BEFORE ", states_before[stype] )
        if stype in states_after:
          print_all("AFTER ", states_after[stype]  )


 
  
if __name__ == "__main__":
  args = get_args()
  processed_files = {}
  problems = {}
  states_bef = {}
  states_aft = {}
  
  for filename in args.filename:
      with open(filename, 'rb') as fid:
         data = fid.read()
         data = [ ord(d) for d in data ]
         polar = Polar.Polar( data )
         polar.read_header()
         polar.process()
         processed_files[ filename ] = polar
      print "File '%s' done!" % filename
      for problem in polar.problems:
        dict_problems( polar, problem, problems )
      build_state_machine( polar.samples, states_bef,states_aft )
      
  finish_building( states_bef, states_aft ) 

    
  
  for prefix, prob_todo in problems.items():  
     print "-------------- %s ---------------- " % prefix
     for prob in prob_todo :
         print "PROBLEM :" + str( prob[0] ) + " - bef: " + str(prob[1])  + " aft: " + str(prob[2])
     
  for prefix in problems:  
    print "prefix: %s : %d " % (prefix, len(problems[prefix]))
    
  
  for fn,polar in processed_files.items():
     print "--------------" + fn + "---------------------"
     string = "".join([ t.short for t in polar.samples])
     print string
  
  
  samples = {}
  for fn,polar in processed_files.items():
     for sample in polar.samples:
       if not isinstance( sample, Polar.TagSample ) :
          continue
       short = ( sample.short[0], sample.data )
       if short not in samples:
         samples[short] = 1
       else:
         samples[short] += 1
  
  
  for shorts, shortd, in sorted( samples ):
    print "('%s',%d,%d), " % (shorts, shortd, samples[shorts, shortd] )
