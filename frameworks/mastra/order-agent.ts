// Stage 24 optional live example. Requires the isolated package install described in README.
import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

export function totalCents(unitCents: number, quantity: number): number {
  if (!Number.isSafeInteger(unitCents) || unitCents < 0 || unitCents > 100000000 ||
      !Number.isSafeInteger(quantity) || quantity < 0 || quantity > 10000) {
    throw new Error('Use bounded integer cents and quantity');
  }
  return unitCents * quantity;
}

async function main() {
  if (!process.argv.includes('--run') || !process.env.OPENAI_API_KEY || !process.env.COURSE_MODEL) {
    throw new Error('Set OPENAI_API_KEY and COURSE_MODEL, then opt in with --run; nothing sent.');
  }
  const orderTotal = createTool({
    id: 'order-total', description: 'Calculate a synthetic order total in integer cents',
    inputSchema: z.object({ unitCents: z.number().int().min(0).max(100000000), quantity: z.number().int().min(0).max(10000) }),
    outputSchema: z.object({ cents: z.number().int() }),
    execute: async ({ unitCents, quantity }) => ({ cents: totalCents(unitCents, quantity) }),
  });
  const agent = new Agent({ id: 'academy-orders', name: 'Academy order assistant',
    instructions: 'Use orderTotal for synthetic order arithmetic. Never place orders.',
    model: `openai/${process.env.COURSE_MODEL}`, tools: { orderTotal } });
  console.log((await agent.generate('Total three units at 1250 cents each.')).text);
}
void main();
