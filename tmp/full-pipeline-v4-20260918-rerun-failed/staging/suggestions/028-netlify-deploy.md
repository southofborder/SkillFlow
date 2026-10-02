# 028-netlify-deploy · 当前图核对意见

本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。

- 样例：R04；运行：full-pipeline-v4-20260918-rerun-failed；选图轮次：0
- 执行来源：本次重新执行；父运行：`full-pipeline-v4-20260918`；实际执行运行：`full-pipeline-v4-20260918-rerun-failed`
- 反馈停止：audit_error；原因：source reference lines are outside unit: src_057
- 安全标注：invalid_response；原因：evidence quote does not match cfg location g_0070
- 图 SHA-256：60e68d82736a248df1881ab5f63c149d305b89d780a92a1321d9050fbb37be3d；源文 SHA-256：f5d7cda215aff150a40f6abe4f15f5d1f7f4d14d188553c038408758930eddcd

未填写保守说明不代表精确保留；覆盖记录不证明语义完整。

反馈完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/028/feedback/result.json>)；本地审查页也可展开全文。

安全标注完整执行诊断：[原始运行记录](<D:/projects/SkillFlow/packages/skill-ir/experiments/security_profile/runs/full-pipeline-v4-20260918-rerun-failed/cases/028/annotation/result.json>)；本地审查页也可展开全文。

当前所选图没有合法的完整语义核对记录。不能由结构有效或其他轮次的发现推定通过。

## 助手事后复核

此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。

### 修复轮次 0 · 当前所选图

图 SHA-256：60e68d82736a248df1881ab5f63c149d305b89d780a92a1321d9050fbb37be3d

助手复核完整Skill及三份引用材料、末图27个操作、核对和标注的原始失败原因，并实际查看PNG全图与连续细节。r0图结构及保真有效，但核对与标注响应均被证据校验拒绝；没有可接受的profiles。以下是外置助手意见，未经用户人工确认。

- 核对失败是source reference lines are outside unit: src_057：原始finding_5把SKILL.md 70–74行的引用绑定到不覆盖该范围的单元。标注失败是ir_023的actor/roles证据g_0070引用“Report deployment results to the user”，却未在该定位内出现。二者都是已完整返回的证据格式错误，不是服务未响应；没有自动修引文、丢证据后接收或补跑择优。
- 主图正确保留了初次status、未认证login后再status、认证失败停止；已链接跳过link，未链接按Git remote进行link/失败init；依赖安装在部署之前；按旧站preview/新站或明确请求prod选择；首次和升级权限后的返回分别绑定result_017与result_023，没有混用首次部署URL。
- 确有可分析过程缺口：SKILL.md要求尽可能从package.json检测框架并建议适当设置，但图中只有ir_020的netlify.toml/用户提示约束，没有可定位的package.json框架检测。Error Handling中的Build failed后检查配置/依赖/日志，以及Publish directory not found后的构建与路径核查也没有操作、边或相关条件声明；当前只有成功与network error两条部署出口。不能把源码未嵌入的这些段落视为图中已包含。
- API Key认证替代及Secrets/dashboard/process.env仅放在图级constraints，未表示对应的可选交互/设置/读取过程；实际unauthenticated路线只进入浏览器login。应明确这些是条件性选项还是当前主流程的一部分，再补其入口与效果，而不是把所有参考命令都无条件展开。Never commit secrets仍是声明，不能推成已经执行了过滤、遮蔽或凭据保护。
- 源文本身有模态张力：主流程允许新站直接production，Tips和deployment-patterns又建议/要求先preview。末图只选主流程规则，没有记录这处范围差异。建议保留原文作用域并标明未决，不能根据常见部署习惯自行决定唯一正确路径或增加批准步骤。
- ir_018引用仅init分支定义的site_is_new，同时约束说明旧站默认preview。结构规则允许部分路径结果依赖，这本身不是非法图；但当前没有精确建模旧站/已链接分支如何提供选择依据，后续传播不能把site_is_new当作所有路径都有实际值。ir_020的两个部署命令是按deployment_type选择的备选文本，不应视作连续两次网络上传。
- ir_020将本地build/upload/返回URL集中在开放操作与metadata/约束内；PNG没有展开内部文件读取和网络发送，不等于这些效果不存在。三个Load As Needed引用文件的大量CLI/config示例也不应全部视为主流程必执行。传播前需明确这种复合动作的分析粒度以及条件触发来源。
- 本例没有被接受的安全标签。原始标注响应保留供诊断，但正式profiles为空且状态invalid_response；不能把27个IR展示为空标签解释为没有安全效果，更不能复用旧图标签。现有图已能支持进一步讨论网络请求/上传和用户报告，但本次不人工补写模型结果。
- 实际查看2517×8992整张PNG及8段连续重叠细节：028/R04/r0、14块、18边、27IR，登录重查、link/init合流、长边、中文状态、报告参数和末尾返回均可读，未见节点边界裁切或文字遮挡。图片显示的是本轮实际末图及失败状态，不是成功替代图。

本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。
