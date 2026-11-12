"""Human-only local approval, bound to an exact proposal file and account database."""
import argparse
import json
from pathlib import Path
from trading_floor import Proposal, TradingFloor

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('proposal_file', type=Path)
    parser.add_argument('--database', required=True)
    parser.add_argument('--reviewer', required=True)
    parser.add_argument('--approve', action='store_true', help='explicit approval after reviewing exact proposal')
    args = parser.parse_args()
    payload=json.loads(args.proposal_file.read_text())
    p=Proposal(**payload.get('proposal', payload))
    floor=TradingFloor(args.database)
    try:
        print(json.dumps({'proposal': payload, 'risk': floor.risk(p)}, indent=2))
        if not args.approve:
            raise SystemExit('Review only: use --approve to record human approval.')
        print(json.dumps(floor.approve(p,args.reviewer),indent=2))
    finally: floor.close()
