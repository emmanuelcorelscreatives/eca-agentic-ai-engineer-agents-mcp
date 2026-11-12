"""Authored semantic regressions; execution belongs to central course QA."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime,timezone

SOURCE=Path(__file__).resolve().parents[1]/'projects/08-mcp-trading-floor/trading_floor.py'
spec=importlib.util.spec_from_file_location('academy_p8_semantic_core',SOURCE)
core=importlib.util.module_from_spec(spec);sys.modules[spec.name]=core;spec.loader.exec_module(core)

class AccountApprovalTests(unittest.TestCase):
 def test_changed_portfolio_requires_new_review(self):
  floor=core.TradingFloor()
  try:
   aca=floor.propose('ACA',5);lab=floor.propose('LAB',5)
   floor.approve(aca,'human');floor.approve(lab,'human');floor.execute(lab,'first')
   with self.assertRaisesRegex(ValueError,'account changed'):floor.execute(aca,'second')
   self.assertEqual(floor.state()['positions'],{'LAB':5})
   floor.approve(aca,'human');floor.execute(aca,'second')
   self.assertEqual(floor.state()['revision'],2)
  finally:floor.close()

 def test_expired_approval_cannot_change_cash(self):
  clock=[100.0];floor=core.TradingFloor(clock=lambda:clock[0])
  try:
   p=floor.propose('ACA',5);floor.approve(p,'human',ttl_seconds=1);clock[0]=102.0
   with self.assertRaisesRegex(ValueError,'expired'):floor.execute(p,'expired')
   self.assertEqual(floor.state()['cash'],'10000.00')
   self.assertEqual(floor.transactions(),[])
  finally:floor.close()

 def test_rejection_and_persistent_proposal_activity(self):
  with tempfile.TemporaryDirectory() as directory:
   database=str(Path(directory)/'paper.sqlite');floor=core.TradingFloor(database)
   p=floor.propose('ACA',5);floor.reject(p,'human','Need stronger evidence');floor.close()
   floor=core.TradingFloor(database)
   try:
    self.assertEqual(floor.proposal_history()[0]['status'],'REJECTED')
    with self.assertRaisesRegex(ValueError,'approval'):floor.execute(p,'denied')
    self.assertEqual(floor.history()[-1]['event'],'human_rejection')
   finally:floor.close()

 def test_explicit_quote_freshness_not_live_fixture_claim(self):
  floor=core.TradingFloor()
  try:
   p=floor.propose('ACA',5)
   fresh=datetime(2026,1,15,16,1,tzinfo=timezone.utc)
   stale=datetime(2026,1,15,17,0,tzinfo=timezone.utc)
   self.assertTrue(floor.risk(p,reference_time=fresh)['allowed'])
   self.assertIn('stale_or_future_quote',floor.risk(p,reference_time=stale)['reasons'])
   self.assertEqual(floor.risk(p)['quote_mode'],'historical fixture replay')
  finally:floor.close()

if __name__=='__main__':unittest.main()
