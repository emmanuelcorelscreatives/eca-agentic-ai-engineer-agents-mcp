"""Finite process-interruption teaching command; execute only on dedicated scratch DB.

prepare-and-crash exits 73 after actual paper execution but before checkpoint commit.
Reconcile mode reads the durable ledger and does not dispatch another trade.
"""
import argparse
import json
import os
from .checkpoints import Checkpoints

def main():
    from trading_floor import TradingFloor
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=['prepare-and-crash','reconcile'])
    p.add_argument('--ledger',required=True); p.add_argument('--checkpoint',required=True)
    args=p.parse_args(); floor=TradingFloor(args.ledger); checkpoints=Checkpoints(args.checkpoint)
    try:
        if args.mode=='prepare-and-crash':
            if floor.db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]: raise ValueError('fresh scratch ledger required')
            proposal=floor.propose('ACA',5)
            floor.approve(proposal,'Academy explicit process-interruption exercise')
            checkpoints.prepare('checkpoint-exercise','checkpoint-paper-order',proposal.digest())
            checkpoints.mark_dispatch('checkpoint-exercise')
            floor.execute(proposal,'checkpoint-paper-order')
            os._exit(73)  # deliberate hard process boundary, not a normal clean shutdown
        print(json.dumps({'checkpoint':checkpoints.reconcile('checkpoint-exercise',floor),'portfolio':floor.state()},sort_keys=True))
    finally: checkpoints.close(); floor.close()

if __name__=='__main__': main()
