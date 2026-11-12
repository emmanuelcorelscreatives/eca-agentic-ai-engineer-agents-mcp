"""Owned stdio fault server for real MCP client timeout/error/malformed tests.

Start via: python -m evaluation_lab.fault_mcp --mode timeout
A client must set a bounded timeout. This module does not contact any provider.
"""
import argparse
import asyncio

def main():
    from mcp.server.fastmcp import FastMCP
    parser=argparse.ArgumentParser(); parser.add_argument('--mode',choices=['normal','timeout','malformed','error'],required=True)
    args=parser.parse_args(); server=FastMCP('Academy owned fault fixture')
    @server.tool()
    async def research_market(symbol:str)->dict:
        if args.mode=='timeout': await asyncio.sleep(60)
        if args.mode=='error': raise RuntimeError('explicit injected local tool error')
        if args.mode=='malformed': return {'synthetic':True,'symbol':symbol,'price':None}
        from trading_floor import TradingFloor
        floor=TradingFloor()
        try: return floor.research(symbol)
        finally: floor.close()
    server.run(transport='stdio')

if __name__=='__main__': main()
