# 028-netlify-deploy｜压缩评审

样例：**R04**；选定轮次：**第 1 次**。

[Skill ZIP](D:/projects/SkillFlow/dataset/skills/028-netlify-deploy.zip) · [CFG PNG](D:/projects/SkillFlow/result/ir-IPP/028-netlify-deploy.png) · [完整评审](D:/projects/SkillFlow/result/suggestions/028-netlify-deploy.md) · [选定 CFG 原记录](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/runs/baseline-deepseek-v4-flash-max-20260910/trials/R04/deepseek-v4-flash-max/1/analysis.json)

**关键过程：**认证与站点关联 → 读取配置/选择部署类型 → Netlify 预览或生产部署 → 返回 URL；网络故障存在条件重跑，禁止将秘密提交 Git 的限制保留。

- **优先补证据：究竟上传什么。** `ir_027/ir_029` 的输入主要是 CLI 资源，所附命令只有 deploy / deploy --prod。配置、发布目录及构建产物到上传内容的关系较弱，影响判断哪些数据到达哪个站点。应从 [SKILL.md:138](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:138)、[SKILL.md:154](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:154) 恢复有依据的关系；无需展开每个构建内部步骤。

- **发布条件存在源文冲突。** [SKILL.md:130](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:130) 的新站生产部署与 [SKILL.md:233](D:/projects/SkillFlow/packages/skill-ir/experiments/semantics_baseline/frozen/corpus/inputs/upstream/netlify-deploy/SKILL.md:233) 的先预览要求需要保留适用范围及冲突。预览 URL 不自动等于私有，生产模式也不直接证明超量；可见范围和当前授权仍需任务/配置证据。

- **纠正旧合流判断，区分秘密的去向。** link/init 与各部署结果可作为可能来源，不能据多 inputs 要求全执行。构建环境使用秘密不等于把秘密打包公开，也不等于已设置成功。需区分认证用途、环境配置、构建读取和发布载荷；认证恢复及 package.json 条件等其余细节交通用回溯。

本页为外置评审意见，按[新版 DOE 需求草案](D:/projects/SkillFlow/result/advice_for_doe/README.md)整理；不作为标准答案，不替代通用语义回溯。
