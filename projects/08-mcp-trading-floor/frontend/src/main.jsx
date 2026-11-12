import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';

function App(){
 const [token,setToken]=useState(''),[reviewToken,setReviewToken]=useState('');
 const [symbol,setSymbol]=useState('ACA'),[quantity,setQuantity]=useState(5);
 const [result,setResult]=useState(null),[account,setAccount]=useState(null),[proposal,setProposal]=useState(null);
 const [error,setError]=useState(''),[loading,setLoading]=useState(false),[requestId,setRequestId]=useState('academy-order-001');
 const [feedbackTarget,setFeedbackTarget]=useState(null),[comment,setComment]=useState(''),[correction,setCorrection]=useState(''),[rating,setRating]=useState(3),[reviewId,setReviewId]=useState('academy-feedback-001');
 async function request(path,body,{review=false}={}){
  setError('');setLoading(true);
  try{
   const headers={'Content-Type':'application/json',...(review?{'X-Academy-Review-Token':reviewToken}:{'X-Academy-Token':token})};
   const response=await fetch('/api'+path,{method:body?'POST':'GET',headers,...(body?{body:JSON.stringify(body)}:{})});
   const data=await response.json();
   if(!response.ok)throw Error(data.detail?JSON.stringify(data.detail):'Request rejected');
   setResult(data);if(data.feedback)setFeedbackTarget(data.feedback);
   return data;
  }catch(e){setError(e instanceof TypeError?'Backend unavailable. Preserve the request ID before retrying a paper order.':e.message);return null;}
  finally{setLoading(false);}
 }
 async function refresh(){const state=await request('/state');if(state)setAccount(state);}
 async function propose(){const data=await request('/proposals',{symbol,quantity,side:'BUY'});if(data)setProposal(data.proposal);}
 async function review(action){if(!proposal)return;const reply=await request('/reviews',{proposal,action,reason:action==='REJECT'?'Reviewer requested stronger evidence':''},{review:true});if(reply!==null)await refresh();}
 async function execute(){if(!proposal)return;const reply=await request('/execute',{proposal,request_id:requestId});if(reply!==null)await refresh();}
 async function feedback(){if(!feedbackTarget)return;await request('/feedback',{submission_id:reviewId,run_id:feedbackTarget.run_id,output_sha256:feedbackTarget.output_sha256,rating,comment,correction:correction||null},{review:true});}
 const box={border:'1px solid #b8c3d4',borderRadius:8,padding:16,marginTop:18};
 return <main style={{fontFamily:'system-ui',maxWidth:1000,margin:'2rem auto',padding:20,lineHeight:1.5}}>
  <h1>Academy synthetic trading floor</h1><p>Fictional companies and paper orders only. Research tools cannot grant human approval.</p>
  <section style={box}><h2>Local access</h2>
   <label>Local course token <input type="password" autoComplete="off" value={token} onChange={e=>setToken(e.target.value)}/></label><br/>
   <label>Separate local reviewer token <input type="password" autoComplete="off" value={reviewToken} onChange={e=>setReviewToken(e.target.value)}/></label>
   <p>Operator and reviewer tokens must differ. This is a local teaching interface, not a public account system.</p>
  </section>
  <section style={box}><h2>Research and proposal</h2>
   <label>Company <select value={symbol} onChange={e=>setSymbol(e.target.value)}>{['ACA','LAB','EDU'].map(s=><option key={s}>{s}</option>)}</select></label>{' '}
   <label>Shares <input type="number" min="1" step="1" value={quantity} onChange={e=>setQuantity(Number(e.target.value))}/></label>{' '}
   <button disabled={loading} onClick={propose}>Research and propose</button>
   {proposal&&<p>Selected exact proposal: {proposal.quantity} {proposal.symbol} at {proposal.price}. Human review is required before execution.</p>}
   <button disabled={loading||!proposal} onClick={()=>review('APPROVE')}>Approve exact proposal</button>{' '}
   <button disabled={loading||!proposal} onClick={()=>review('REJECT')}>Reject exact proposal</button>
   <p><label>Stable paper-order request ID <input value={requestId} onChange={e=>setRequestId(e.target.value)}/></label>{' '}
   <button disabled={loading||!proposal||!requestId} onClick={execute}>Execute approved paper order</button></p>
  </section>
  <section style={box}><h2>Portfolio and activity</h2><button disabled={loading} onClick={refresh}>Read portfolio and trace</button>
   {account&&<><p>Cash: {account.portfolio.cash} · Equity: {account.portfolio.equity} · Revision: {account.portfolio.revision}</p>
    <p>Valuation uses the fixed synthetic snapshot dated {account.portfolio.valuation_as_of}.</p>
    <table><thead><tr><th>Company</th><th>Shares</th></tr></thead><tbody>{Object.entries(account.portfolio.positions).map(([s,q])=><tr key={s}><td>{s}</td><td>{q}</td></tr>)}</tbody></table>
    <p>{account.proposals.length} saved proposals · {account.transactions.length} paper fills</p>
   </>}
  </section>
  <section style={box}><h2>Review a real saved output</h2>
   <p>{feedbackTarget?'Feedback is bound to '+feedbackTarget.run_id:'Generate a proposal or execute an approved order to select a saved output.'}</p>
   <label>Feedback ID <input value={reviewId} onChange={e=>setReviewId(e.target.value)}/></label>{' '}
   <label>Rating <input type="number" min="1" max="5" value={rating} onChange={e=>setRating(Number(e.target.value))}/></label><br/>
   <label>Review comment <textarea value={comment} onChange={e=>setComment(e.target.value)}/></label><br/>
   <label>Suggested correction <textarea value={correction} onChange={e=>setCorrection(e.target.value)}/></label><br/>
   <button disabled={loading||!feedbackTarget||!comment.trim()} onClick={feedback}>Save reviewer feedback</button>
  </section>
  {loading&&<p role="status">Working…</p>}{error&&<p role="alert">{error}</p>}
  <h2>Observed response</h2><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{JSON.stringify(result,null,2)}</pre>
  {account&&<details><summary>Persisted proposals, transactions and trace</summary><pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(account,null,2)}</pre></details>}
 </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
