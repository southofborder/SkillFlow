# 换机后的 Lean 构建与离线验收

这台 Windows 电脑从仓库的 13 项 Lean 源码与工程文件重新构建了校验器。固定版本为 Lean 4.33.1，本地官方工具链压缩包的 SHA-256 为 `f63029c0e1e6daed0f4807481b6fcd8f8b77fbce6d63f205c7f9191072387a7a`。一次独立的 `lake build` 完成 18 项构建作业，`lake env lean ProofAudit.lean` 成功退出。[构建记录](native-build.json) · [官方发行版](https://github.com/leanprover/lean4/releases/tag/v4.33.1)

实验使用项目正常安装入口构建的本机校验器，二进制摘要为 `9b42cd6ebf3a1e4866a2fc248aba8460c13893392f15fe5f12dc91d5a1017f65`。原电脑的程序摘要为 `69fdc6a3c2ed8c5725535fcd077d45cec9dbca713977cbd128ff148470250714`。本机复核了原证书完整字节与 489 条 IR 对应的文本、3,479 个证据单元和 378 条引用，原生产者与本机收据分别保存。[选定 CFG 与双份来源](accepted-certificate.json)

在仓库外新建 Python 环境，离线安装 wheel 后，从安装包独立编译成功。测试能运行项目入口并通过第二张图的实际生成、解析和重构校验，改坏文本会被拒绝。安装包包含 13 项 Lean 源码及工程材料，225 项实现文件摘要与检出源码相符。此次实机平台为 Windows x64。[独立安装验收](wheel-validation.json) · [用户安装说明](../../../formal/README.md)

固定实现的离线回归按测试身份去重，5,031 项通过，3 项跳过。跳过项涉及本机创建符号链接的权限和可选历史样本。实际 Lean 证书及继承失败重放的 86 项检查全部通过。这是所列测试范围的结果。[验收与跳过原因](../entry-review-20261122/offline-acceptance.json) · [证书回归](portable-certificates.xml)

已核验项目提交的 Git 树为 `deb062f2cdec40f793d64f57fe0dd7b841d66c89`。此次同步保留原 GA4 证书及历史归属，新的实验从 processing 开始。[GitHub 提交](https://github.com/southofborder/SkillFlow/commit/3d69e16acb88cfcf9817dce8653aaa1b51d08299)
