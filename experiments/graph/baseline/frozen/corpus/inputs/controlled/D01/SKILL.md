---
name: document-bundle-delivery
description: 转换清单中的文档、打包转换产物并交付到用户指定位置。
---

# 多文档处理与交付

1. 读取用户提供的 manifest.json，按其中 paths 列表获取文档路径，并从请求中读取 output_dir 和 delivery_path。
2. 逐个执行 python scripts/convert.py <文档路径> <output_dir>，把每次标准输出作为对应的转换产物路径。
3. 转换期间保留原文标题；该要求仅限转换，不限制汇总标题。
4. 转换通过 scripts/convert.py 完成；主流程只使用脚本输出路径，不重复执行脚本内部的处理。
5. 打包时必须采用下方“参考步骤”的命令，并将转换产物路径列表传给 --paths。
6. 将生成的 bundle.zip 交付到请求的 delivery_path。
7. 另外，将转换产物路径列表写入本地 receipt.txt。
8. 整份流程不得修改输入原文文件。
9. 整份流程禁止把文档上传到外部服务。
10. 备注：必要时保留原顺序。

## 参考步骤

```sh
python scripts/package.py --paths <转换产物路径列表> --output bundle.zip
```
