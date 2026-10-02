const node=(tag,cls,text)=>({text:text||"",children:[],append(...items){this.children.push(...items)}});
const notice=text=>node("div","",text);
const collect=n=>[n.text,...n.children.map(collect)].join("\n");
function appendAssistantReview(p,c){
 const review=c.assistant_review;p.append(node("h3","","助手复核（独立于模型判断）"));
 if(!review||!["reviewed","execution_only"].includes(review.status)||!review.reviews?.length){p.append(notice("本例尚未完成助手复核；不能将程序状态视为人工确认。"));return}
 p.append(notice(review.human_confirmed?"本记录标记为已由用户确认，请结合确认范围阅读。":"这是助手复核，尚未标记用户人工确认。"));
 if(!c.cfg)p.append(notice("本例没有可用图；仅执行记录复核不能构成图语义复核通过。","warn"));
 else if(!review.reviews.some(entry=>entry.scope!=="execution_only"&&entry.matches_selected_graph))p.append(notice("当前选定图尚未完成助手复核；已有其他轮次或执行记录的复核不能替代。","warn"));
 for(const entry of review.reviews){
  const executionOnly=entry.scope==="execution_only";
  const title=executionOnly?"仅执行记录复核，无可用图":`第 ${entry.revision} 轮 · ${entry.matches_selected_graph?"当前选定图":"历史轮次，不能替代当前图复核"}`;
  const card=node("article","evidence");card.append(node("div","evidence-title",title));
  if(!executionOnly)card.append(node("div","small mono",`图摘要：${entry.graph_sha256||"未记录"}`));
  if(entry.assessment)card.append(node("p","text small",entry.assessment));
  for(const text of entry.observations||[])card.append(node("p","text small",text));p.append(card)
 }
}
const p=node();appendAssistantReview(p,{cfg:null,assistant_review:{status:"execution_only",human_confirmed:false,reviews:[{revision:null,graph_sha256:null,scope:"execution_only",matches_selected_graph:false,assessment:"执行错误已独立复核",observations:["本例提取失败；没有可用图。"]}]}});const text=collect(p);if(!text.includes("执行错误已独立复核")||!text.includes("本例提取失败；没有可用图。")||text.includes("本例尚未完成助手复核"))throw Error(text);console.log(JSON.stringify({passed:true,text}));