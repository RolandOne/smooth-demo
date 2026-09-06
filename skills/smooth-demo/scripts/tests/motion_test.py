import importlib.util,pathlib,unittest,tempfile
from PIL import Image
S=pathlib.Path(__file__).resolve().parents[1]
def load(name):
 sp=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
r=load('render-motion');p=load('plan-motion')
class MotionTest(unittest.TestCase):
 def test_curve_has_exact_endpoints_and_bends(self):
  keys=[{'time':0,'x':0,'y':0},{'time':1,'x':100,'y':0,'kind':'hand'}]
  self.assertEqual(r.cursor_at(0,keys,.16)[:2],(0,0));self.assertEqual(r.cursor_at(1,keys,.16),(100,0,'hand'));self.assertGreater(r.cursor_at(.5,keys,.16)[1],0)
 def test_text_state_and_all_sprite_hotspots(self):
  self.assertEqual(r.cursor_at(.5,[{'time':0,'x':30,'y':30,'kind':'text'},{'time':1,'x':30,'y':30}],.16)[2],'text')
  for im,hot in r.cursor_sprites(40).values():self.assertTrue(0<=hot[0]<im.width and 0<=hot[1]<im.height)
 def test_negative_and_nonfinite_times_rejected(self):
  for t in [-.1,float('nan')]:
   with self.assertRaises(ValueError):r.check_keys([{'time':t,'x':0}],['x'])
 def test_planner_zooms_out_before_navigation(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);Image.new('RGB',(1440,900)).save(root/'frame.jpg')
   d={'duration':12,'frames':[{'file':'frame.jpg','time':0}],'events':[{'name':'click-email','time':3,'x':1000,'y':400},{'name':'zoom-out','time':6},{'name':'click-sign-in','time':8,'x':1000,'y':550}]}
   cfg=p.plan(root/'capture.json',d);self.assertGreater(max(k['zoom'] for k in cfg['camera']),1);self.assertEqual(r.tween(8,cfg['camera'],['zoom'])[0],1);self.assertEqual(cfg['cursor'][1]['kind'],'text')
if __name__=='__main__':unittest.main()
