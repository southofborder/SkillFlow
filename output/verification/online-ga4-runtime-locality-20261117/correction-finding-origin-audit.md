# Processing correction: origin of later review findings

This passive audit compares the expanded saved a001/a002 processing answers from **this run only**, against the original annotation findings retained in the accepted initial source review. It does not execute or validate either candidate. Exact target pointers, before/after hashes, changed fields, local producer links, CFG operands and original source references are in `correction-finding-origin-audit.json` (SHA256 `e6a23021ce894134e0c2820bb6fa0412802e4d73e9353c68e817a5df325d0638`).

| Later finding | Exact target comparison | What the evidence supports |
|---|---|---|
| F010, returned report values | 19 output bindings changed `local reply` → `local x` | This specific output misbinding appeared in the full replacement answer. Both versions still define `x` as the `parseGA` / `reports.parseDateRange` return, `tuple` as the remote report return, and `reply` as `tuple[0]`. Both still save `reply`. It is not a variable rename. |
| F011, missing actual receiver | Five call records differ, but op/location/input refs/output are identical | The receiver omission is already present in a001. The five CFGs supply a client operand; both versions' call bindings still use only the request. Other record changes alone do not establish regression. |
| F012, environment update | One exact target unchanged | The later finding's call target predates replacement. This comparison does not certify all external location/state relations. |
| F013, save argument/address dependencies | Ten exact write targets unchanged | The identified write operands predates replacement; target equality is not a claim that every ancestor/location record is unchanged. |
| F014, directory path as payload | One exact write target unchanged | The specific path-as-content representation is already present. |
| F015, opaque listing/loading summaries | Two call records differ, but call bindings are identical | The coarse call representation already exists in both versions. Full-record differences do not show that replacement introduced the missing internal acquisition boundaries. |
| F016, omitted console completion effects | Two complete IR records unchanged | The empty completion records already exist in a001. |
| F017–F019, mapping/sensitivity | Nine targets belong to other fragments | Incomparable to the two processing answers; no origin claim is made. |

F010 targets `/ir_semantics/<IR>/output_bindings/0` for `ir_106`, `110`, `114`, `118`, `122`, `126`, `358`, `359`, `360`, `361`, `368`, `369`, `370`, `377`, `378`, `379`, `386`, `387`, `388` (each identifier has the `ir_` prefix). All nineteen producer relationships were checked in the saved JSON, even where segment positions changed. Frozen source `skill/scripts/src/api/reports.ts:90–108` puts the parsed range in the request and returns the SDK response; lines 114–175 return `runReport` from the wrappers. `skill/scripts/src/index.ts:55–166` stores those returned wrapper values in higher-level reports. This supports a concrete newly introduced wrong-output relation, without claiming that the whole a001 answer was correct: a001 itself failed structural validation.

Totals: **19 changed output bindings, 7 changed call records with unchanged defect-relevant call bindings, 14 exactly unchanged processing targets, and 9 other-fragment targets**. These cover 10 original annotation findings, seven processing-owned. The newer error at `ir_001` discussed in earlier reports is a different case: its processing record was unchanged and its reference error was newly exposed by deeper validation.

No inference is made that a narrower hypothetical patch would have passed, that all changed records regressed, or that these errors have already produced a runtime/deletion outcome. The audit does not determine why the model selected the altered output names. No frozen file, original response or existing report was changed.

**中文结论：** 不能把本轮所有问题都归因于原稿，也不能把所有记录差异都叫退化。F010 的 19 处返回绑定有明确的新变化：a001 返回仍存在的 `reply`，a002 改为仍表示日期范围的 `x`，保存却继续使用 `reply`；源文明确返回报告响应，因此这是全量纠错答复中出现的具体错绑。另有 14 个 processing 目标完全未变，7 个 call 目标虽整体记录不同但缺陷相关的调用绑定未变；mapping/sensitivity 的 9 个目标不能用 processing 两版判断来源。a001 本身未通过结构校验，以上并不证明旧稿整体正确或局部纠错必然成功。全程仅只读解析，没有运行校验器、后端、模型、Skill 或重放。
