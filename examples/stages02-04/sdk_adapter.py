"""Optional OpenAI Python SDK Chat Completions boundary.
Install the optional `openai` package in your own virtual environment.
No SDK is required for the offline labs. No model name is assumed available.
"""
import os


class OpenAISDKModel:
    def __init__(self, *, model, base_url=None, allow_live=False, client=None):
        if not allow_live or not model:
            raise ValueError('Explicit live opt-in and model required')
        if client is None:
            from openai import OpenAI
            from foundations import api_key
            client = OpenAI(api_key=api_key(), base_url=base_url, timeout=20, max_retries=0)
        self.client, self.model = client, model

    def chat(self, messages, tools=None):
        kwargs = {'model': self.model, 'messages': messages, 'max_completion_tokens': 256}
        if tools:
            kwargs['tools'] = tools
        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        if choice.finish_reason not in ('stop', 'tool_calls'):
            raise ValueError('Incomplete generation')
        return choice.message.model_dump(exclude_none=True)
