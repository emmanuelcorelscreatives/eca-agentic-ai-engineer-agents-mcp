import { Mastra } from '@mastra/core/mastra';
import { buildAgent,workflow } from '../../triage.js';
const model=process.env.COURSE_MODEL;
if(!model) throw new Error('Set COURSE_MODEL to a provider/model ID before starting Studio');
export const mastra=new Mastra({agents:{triage:buildAgent(model)},workflows:{triage:workflow}});
