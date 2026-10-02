from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
reviews={
'027': (
'助手复核完整源文及脚本、四轮关键变化、末图29个操作和全部安全标注，并实际查看PNG全图与连续细节。末图结构及受控保真有效，但第3轮核对因许可证引文行号错误被拒绝，不能称核对通过。以下意见未经用户人工确认。',
[
'停止原因已核实：r3 原始 finding_1 引 LICENSE.txt 第74行，却引用实际第75行的 worldwide, non-exclusive, no-charge, royalty-free, irrevocable。属于真实引文位置错误，不是网络故障、图结构错误或该业务项已确认错转；其余原始发现也不能越过响应有效性门槛升级为已接受结论。标注 complete 与这一失败独立。',
'末图保留 repo默认值、pr可选/当前分支、认证前置、首选脚本与手动替代、外部provider只报URL、缺日志说明、计划审批后实施以及只建议重检。ir_009完整保存15222字符的原脚本；其实际输出分为 stdout/error/exit-code，ir_013手动路径保留字段漂移重试和pending时job-log命令。控制连接完整显示，未把所有引用命令都额外执行一遍。',
'r0遗漏手动替代路径的反馈有原文依据。r2发现“任何非零退出都等于checks失败”也有依据：脚本的配置、认证、API等错误同样返回1；r3的edges/6与edges/7区分错误停止和失败检查继续，修复了该分支混淆。stderr/exit-code接口仍需按脚本真实输出理解，不能根据标签宣称所有错误均被精确分类。',
'r0 finding_11 和r1 finding_7在无失败路径的返回身份上反复：把外层Skill的return与嵌入Python main返回值混为同一层，可能过严。r0的inspection_report是工具结果名字，不能仅凭名字断言不是无失败stdout；r1又要求去掉stdout只返回exit-code。r3现有ir_011返回工具inspection_output且块约束注明no failing消息，尚无有效核对结论。建议先固定外层Skill输出与stdout/exit-code的接口含义，不把更名当成正确性证明。',
'r0未批准时return fix_plan被判新增，需与“额外向用户发送计划”区分；普通return不是user_output。末图ir_023为空返回，明确批准边才进入ir_024，审批边界保留。申请批准ir_021同时生成approval_decision，后续传播应显式理解这是交互所得新信息，不从模型生成计划直接推得批准。',
'ir_015的两个输入result_005/result_008分别来自互斥的脚本/手动分支，是有控制依据的候选依赖，不能当作两者同时传参或结构非法；r1/r2核对也曾明确保守合流。分类操作仅声明非GitHub Actions不进一步查询，不能据此证明真实URL主机验证或保护动作已经执行。',
'29个profile均有合法引用。ir_007/009/013的网络发送与接收有具体gh/GitHub请求依据，比仅凭工具名称推网络更强；ir_013的fs_write对应pending-job-log分支的重定向，是条件可能效果。ir_009工具结果回传支持EM02下的model_observe，但不代表完整远端日志全部进入模型；默认max-lines/context和JSON/text模式影响回传对象，也不证明日志已脱敏。',
'标注中的执行与观察仍有推断边界：ir_015仅据分类动作就认定llm，ir_024理由为“模型或代理”却只列llm；EM04本身不能证明前提。ir_021产生用户批准结果却只有sink，没有source/context_read或human参与说明，可能遗漏交互输入角色。ir_017源文明示Summarize failures for the user，而profile仅transform/model_observe，没有sink/user_output，属值得优先核实的漏标；ir_025面向用户的报告也存在相近边界。不要据unresolved=[]宣称这些推断已确定。',
'实际查看2531×8221整张PNG及8段重叠细节：027/R03/r3、15块、15边、29IR，中文标题和状态、长英文约束、脚本/手动分叉、三种退出及审批路径清晰，未见节点文本或箭头被裁切。PNG不展示脚本全文，完整源码在审查材料中另存。'
]),
'028': (
'助手复核完整Skill及三份引用材料、末图27个操作、核对和标注的原始失败原因，并实际查看PNG全图与连续细节。r0图结构及保真有效，但核对与标注响应均被证据校验拒绝；没有可接受的profiles。以下是外置助手意见，未经用户人工确认。',
[
'核对失败是source reference lines are outside unit: src_057：原始finding_5把SKILL.md 70–74行的引用绑定到不覆盖该范围的单元。标注失败是ir_023的actor/roles证据g_0070引用“Report deployment results to the user”，却未在该定位内出现。二者都是已完整返回的证据格式错误，不是服务未响应；没有自动修引文、丢证据后接收或补跑择优。',
'主图正确保留了初次status、未认证login后再status、认证失败停止；已链接跳过link，未链接按Git remote进行link/失败init；依赖安装在部署之前；按旧站preview/新站或明确请求prod选择；首次和升级权限后的返回分别绑定result_017与result_023，没有混用首次部署URL。',
'确有可分析过程缺口：SKILL.md要求尽可能从package.json检测框架并建议适当设置，但图中只有ir_020的netlify.toml/用户提示约束，没有可定位的package.json框架检测。Error Handling中的Build failed后检查配置/依赖/日志，以及Publish directory not found后的构建与路径核查也没有操作、边或相关条件声明；当前只有成功与network error两条部署出口。不能把源码未嵌入的这些段落视为图中已包含。',
'API Key认证替代及Secrets/dashboard/process.env仅放在图级constraints，未表示对应的可选交互/设置/读取过程；实际unauthenticated路线只进入浏览器login。应明确这些是条件性选项还是当前主流程的一部分，再补其入口与效果，而不是把所有参考命令都无条件展开。Never commit secrets仍是声明，不能推成已经执行了过滤、遮蔽或凭据保护。',
'源文本身有模态张力：主流程允许新站直接production，Tips和deployment-patterns又建议/要求先preview。末图只选主流程规则，没有记录这处范围差异。建议保留原文作用域并标明未决，不能根据常见部署习惯自行决定唯一正确路径或增加批准步骤。',
'ir_018引用仅init分支定义的site_is_new，同时约束说明旧站默认preview。结构规则允许部分路径结果依赖，这本身不是非法图；但当前没有精确建模旧站/已链接分支如何提供选择依据，后续传播不能把site_is_new当作所有路径都有实际值。ir_020的两个部署命令是按deployment_type选择的备选文本，不应视作连续两次网络上传。',
'ir_020将本地build/upload/返回URL集中在开放操作与metadata/约束内；PNG没有展开内部文件读取和网络发送，不等于这些效果不存在。三个Load As Needed引用文件的大量CLI/config示例也不应全部视为主流程必执行。传播前需明确这种复合动作的分析粒度以及条件触发来源。',
'本例没有被接受的安全标签。原始标注响应保留供诊断，但正式profiles为空且状态invalid_response；不能把27个IR展示为空标签解释为没有安全效果，更不能复用旧图标签。现有图已能支持进一步讨论网络请求/上传和用户报告，但本次不人工补写模型结果。',
'实际查看2517×8992整张PNG及8段连续重叠细节：028/R04/r0、14块、18边、27IR，登录重查、link/init合流、长边、中文状态、报告参数和末尾返回均可读，未见节点边界裁切或文字遮挡。图片显示的是本轮实际末图及失败状态，不是成功替代图。'
])}
for case,(assessment,observations) in reviews.items():
 row=json.loads((ROOT/f'preview-{case}/review-data.json').read_text(encoding='utf-8'))['cases'][0]
 doc={'run_id':row['run_id'],'case_id':case,'reviews':[{'revision':row['selected_revision'],'graph_sha256':row['graph_sha256'],'assessment':assessment,'observations':observations}]}
 out=ROOT/'assistant-reviews'/f'{case}.json'
 assert not out.exists(),out
 out.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
