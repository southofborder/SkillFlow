# 阿里云服务清单（报销附件）

- `aliyun-bill-template.tex`：简洁版 LaTeX 模板。
- `aliyun-bill-template.pdf`：编译后的示例预览。

修改源文件的“基本信息”和“服务明细”即可。金额直接以人民币元填写，并同步修改 `\TotalAmount` 合计。表格状态与创建时间均指订单，方便与付款记录核对。

源文件采用 UTF-8 编码，使用 XeLaTeX 编译两次：

```shell
xelatex -interaction=nonstopmode -halt-on-error aliyun-bill-template.tex
```

示例数据用于展示格式，使用时替换为实际信息；费用所属期间和关联发票号码在表格上方统一填写。
