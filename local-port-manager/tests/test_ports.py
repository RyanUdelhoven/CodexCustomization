import concurrent.futures
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ports.py'
class PortsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.db=self.root/'state/ports.sqlite3'
 def tearDown(self): self.tmp.cleanup()
 def run_cli(self,*args,ok=True):
  r=subprocess.run([sys.executable,str(SCRIPT),'--registry',str(self.db),*map(str,args)],capture_output=True,text=True)
  if ok:
   self.assertEqual(r.returncode,0,r.stderr); return json.loads(r.stdout)
  self.assertNotEqual(r.returncode,0); return r
 def allocate(self,service,*args):
  return self.run_cli('allocate','--project',self.root,'--service',service,*args)
 def test_inspection_no_creation(self):
  self.assertEqual(self.run_cli('list'),[]); self.assertFalse(self.db.exists())
 def test_reuse_release_and_transport(self):
  a=self.allocate('web'); self.assertEqual(self.allocate('web')['port'],a['port'])
  self.run_cli('allocate','--project',self.root,'--service','other','--port',a['port'],ok=False)
  self.assertEqual(self.allocate('udp','--protocol','udp','--port',a['port'])['port'],a['port'])
  self.run_cli('release','--project',self.root,'--service','web')
  self.assertEqual(self.allocate('replacement','--port',a['port'])['port'],a['port'])
 def test_occupied_and_adoption(self):
  with socket.socket() as listener:
   listener.bind(('127.0.0.1',0)); listener.listen(); port=listener.getsockname()[1]
   self.run_cli('allocate','--project',self.root,'--service','web','--port',port,ok=False)
   self.assertFalse(self.allocate('web','--port',port,'--adopt-occupied')['bind_available'])
   self.assertTrue(self.allocate('web')['reused'])
   self.assertFalse(self.run_cli('check')[0]['bind_available'])
 def test_concurrent_allocations(self):
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
   rows=list(pool.map(lambda i:self.allocate('service'+str(i)),range(12)))
  self.assertEqual(len({r['port'] for r in rows}),12)
  self.assertEqual(len(self.run_cli('list')),12)
 def test_failure_preserves_state(self):
  row=self.allocate('web')
  self.run_cli('allocate','--project',self.root,'--service','web','--port',row['port']+1,ok=False)
  self.assertEqual(self.run_cli('list')[0]['port'],row['port'])
  self.run_cli('allocate','--project',self.root,'--service','bad','--minimum',2,ok=False)
 def test_release_retired_directory(self):
  retired=self.root/'retired'; retired.mkdir()
  self.run_cli('allocate','--project',retired,'--service','web')
  retired.rmdir()
  self.assertIsNotNone(self.run_cli('release','--project',retired,'--service','web')['released'])
 def test_corrupt_registry_not_replaced(self):
  self.db.parent.mkdir(); self.db.write_text('invalid database')
  self.run_cli('allocate','--project',self.root,'--service','web',ok=False)
  self.assertEqual(self.db.read_text(),'invalid database')
if __name__=='__main__': unittest.main()
