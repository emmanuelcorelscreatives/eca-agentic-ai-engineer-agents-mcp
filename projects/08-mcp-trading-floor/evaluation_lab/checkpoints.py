"""Durable intent/checkpoint state for paper-order reconciliation after interruption."""
import json
import sqlite3

class Checkpoints:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS workflow_checkpoint(run_id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, proposal_digest TEXT NOT NULL, state TEXT NOT NULL, result TEXT)')

    def prepare(self,run_id,request_id,proposal_digest):
        with self.db:
            old=self.db.execute('SELECT request_id,proposal_digest FROM workflow_checkpoint WHERE run_id=?',(run_id,)).fetchone()
            if old and tuple(old)!=(request_id,proposal_digest): raise ValueError('checkpoint identity changed')
            self.db.execute("INSERT OR IGNORE INTO workflow_checkpoint VALUES (?,?,?,'PREPARED',NULL)",(run_id,request_id,proposal_digest))

    def mark_dispatch(self,run_id):
        with self.db:
            cursor=self.db.execute("UPDATE workflow_checkpoint SET state='WRITE_INTENT' WHERE run_id=? AND state='PREPARED'",(run_id,))
            if cursor.rowcount != 1: raise ValueError('dispatch requires fresh prepared checkpoint')

    def reconcile(self,run_id,floor):
        row=self.db.execute('SELECT request_id,proposal_digest,state,result FROM workflow_checkpoint WHERE run_id=?',(run_id,)).fetchone()
        if row is None: raise ValueError('unknown checkpoint')
        order=floor.db.execute('SELECT digest,result FROM orders WHERE request_id=?',(row[0],)).fetchone()
        if order:
            if order['digest']!=row[1]: raise ValueError('ledger/checkpoint digest mismatch')
            result=json.loads(order['result'])
            with self.db: self.db.execute("UPDATE workflow_checkpoint SET state='COMMITTED',result=? WHERE run_id=?",(json.dumps(result,sort_keys=True),run_id))
            return {'state':'COMMITTED','result':result,'dispatch_allowed':False}
        # Absence alone does not prove an old writer cannot still commit.
        return {'state':'UNRESOLVED' if row[2]=='WRITE_INTENT' else row[2], 'dispatch_allowed':row[2]=='PREPARED'}

    def close(self): self.db.close()
