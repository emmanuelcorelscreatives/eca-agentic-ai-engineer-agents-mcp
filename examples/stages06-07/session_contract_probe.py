"""Real SDK Runner/SQLite restart probe using an explicitly synthetic local Model.

This exercises SDK history delivery, not model intelligence. It never calls a
provider and its synthetic response has no provider response ID or token claim.
"""
import argparse
import asyncio
import json

from agents import Agent, Runner, RunConfig, SQLiteSession
from agents.items import ModelResponse
from agents.models.interface import Model
from agents.usage import Usage
from openai.types.responses import ResponseOutputMessage, ResponseOutputText


class HistoryObservationModel(Model):
    def __init__(self):
        self.observed_input = None

    async def get_response(self, system_instructions, input, *args, **kwargs):
        self.observed_input = input
        payload = json.dumps({'synthetic_model': True,
                              'prior_marker_present': 'SELECTED:ECA-101' in json.dumps(input)})
        output = ResponseOutputMessage(id='synthetic-history-observation', type='message',
            role='assistant', status='completed',
            content=[ResponseOutputText(type='output_text', text=payload, annotations=[])])
        return ModelResponse(output=[output], usage=Usage(), response_id=None)

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError('This synthetic history probe does not implement streaming')
        yield  # Keep the required abstract interface an async iterator; never executed.


async def probe(path: str, step: str):
    if step not in {'seed', 'followup', 'control'}:
        raise ValueError('invalid probe step')
    model = HistoryObservationModel()
    agent = Agent(name='Synthetic SDK history contract', model=model)
    session = SQLiteSession('academy-contract' if step != 'control' else 'unrelated-contract', db_path=path)
    result = await Runner.run(agent, 'SELECTED:ECA-101' if step == 'seed' else 'What was selected?',
                              session=session, run_config=RunConfig(tracing_disabled=True), max_turns=1)
    return {'origin': 'actual-sdk-runner-with-explicit-synthetic-model', 'step': step,
            'provider_calls': 0, 'result': json.loads(result.final_output),
            'stored_items': len(await session.get_items())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--step', choices=['seed', 'followup', 'control'], required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(probe(args.db, args.step))))
