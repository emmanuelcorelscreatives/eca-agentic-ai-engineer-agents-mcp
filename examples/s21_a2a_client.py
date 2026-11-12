"""Independent A2A SDK1.3 HTTP client. Provider-free, actual protocol exchange."""
import asyncio
async def main():
    import httpx
    from a2a.client import A2ACardResolver, ClientConfig, create_client
    from a2a.helpers import new_text_message
    from a2a.types import Role, SendMessageRequest
    async with httpx.AsyncClient(timeout=5.0) as http:
        card=await A2ACardResolver(httpx_client=http,base_url='http://127.0.0.1:8765').get_agent_card()
        if {skill.id for skill in card.skills}!={'stock-check'}:
            raise ValueError('Unexpected skill set')
        client=await create_client(agent=card,client_config=ClientConfig(streaming=False))
        request=SendMessageRequest(message=new_text_message('ECA-KEY-01',role=Role.ROLE_USER))
        try:
            async with asyncio.timeout(5):
                async for result in client.send_message(request):
                    print(result)
        finally:
            await client.close()
if __name__=='__main__':
    asyncio.run(main())
