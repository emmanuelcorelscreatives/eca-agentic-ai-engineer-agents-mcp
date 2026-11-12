"""Explicit retention and outbox operations; no implicit daemon or remote retry."""
import argparse
import json
import time
from config import Settings
from tools import ToolsService

def maintain(settings,operation):
    with ToolsService(settings.database) as tools:
        if operation=='purge':return tools.purge_retention(time.time()-settings.retention_days*86400)
        if operation=='outbox':return tools.pending_outbox()
        if operation=='dry-run-one':return tools.dispatch_once()
        raise ValueError('unknown maintenance operation')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['purge','outbox','dry-run-one']);args=parser.parse_args()
    print(json.dumps(maintain(Settings.from_env(),args.operation),indent=2))
