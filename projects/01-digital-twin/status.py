"""Visible action state, never hidden reasoning or personal contact contents."""
from dataclasses import dataclass,field
import uuid

@dataclass
class Checklist:
    task_id:str=field(default_factory=lambda:uuid.uuid4().hex)
    steps:dict=field(default_factory=lambda:{'consent':'pending','validation':'pending','storage':'pending','notification':'pending'})
    terminal:str='pending'
    def update(self,step,state):
        if step not in self.steps or state not in ('pending','passed','failed','not_requested','queued','unknown'):raise ValueError('unknown checklist step or state')
        self.steps[step]=state
    def finish(self,status):
        if status not in ('complete','failed','consent_required','unknown'):raise ValueError('unknown terminal status')
        if status=='complete' and (self.steps['consent']!='passed' or self.steps['validation']!='passed' or self.steps['storage']!='passed'):raise ValueError('cannot complete before consent, validation and storage succeed')
        self.terminal=status
    def visible(self):
        return {'task_id':self.task_id,'steps':dict(self.steps),'terminal':self.terminal}
