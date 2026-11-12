import unittest,tempfile
from pathlib import Path
from coursekit.core import Tool,ToolRegistry,run_agent,Sessions,score_grounding

class CoreTests(unittest.TestCase):
 def registry(self):
  return ToolRegistry([Tool('double','Double an integer',{'properties':{'value':{'type':'integer'}},'required':['value']},lambda value:value*2)])
 def test_loop_actual_result(self):
  def model(messages):
   if len(messages)==1:return {'tool_calls':[{'id':'a','name':'double','arguments':{'value':5}}]}
   return {'text':messages[-1]['content']}
  result=run_agent(model,'double five',self.registry())
  self.assertEqual(result.events[0]['result'],10)
  self.assertIn('10',result.text)
 def test_type_and_unknown_fail_closed(self):
  for arguments in ({'value':True},{'value':'5'},{'value':3,'other':4},{}):
   from coursekit.core import ToolRequest
   with self.assertRaises(ValueError):self.registry().execute(ToolRequest('x','double',arguments))
 def test_human_approval(self):
  from coursekit.core import ToolRequest
  touched=[];registry=ToolRegistry([Tool('send','External action',{'properties':{}},lambda:touched.append(1),True)])
  with self.assertRaises(PermissionError): registry.execute(ToolRequest('a','send',{}))
  self.assertEqual(touched,[])
 def test_no_endless_loop(self):
  i=iter(range(10))
  result=run_agent(lambda m:{'tool_calls':[{'id':str(next(i)),'name':'double','arguments':{'value':2}}]},'loop',self.registry(),max_steps=2)
  self.assertEqual(result.stopped_reason,'step_budget');self.assertEqual(len(result.events),2)
 def test_sessions_persist_isolate(self):
  with tempfile.TemporaryDirectory() as folder:
   path=str(Path(folder)/'s.db');s=Sessions(path);s.append('a',{'n':1});s.append('b',{'n':2});s.close()
   s=Sessions(path);self.assertEqual(s.load('a'),[{'n':1}]);s.close()
 def test_grounding_does_not_invent(self):
  result=score_grounding([{'source_id':'a','excerpt':'real'},{'source_id':'a','excerpt':'invented'}],{'a':'A real synthetic source.'})
  self.assertEqual(result['supported'],1)

if __name__=='__main__':unittest.main()
