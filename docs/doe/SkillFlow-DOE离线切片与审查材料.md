# DOE 切片的当前职责

切片算法保留在 `skillflow.doe.material`，为反向需求及报告构造提供只读关联事实。独立切片 prepare/replay 命令、运行包装和专用调度已经退役。

输入通过 `load_propagation_materials()` 取得：源文、CFG、原始及编译标注来自明确的上游引用，Data、记录和实际 sink 来自传播自己的文件。不创建另一份包含所有内容的总包。公共加载器核验引用、调用链、编译、数据关系、状态和 sink 覆盖。

保留的关系包括来源与实际载荷的区别、直接内容与 possible 影响、删除和覆盖、逐元素配对、条件与候选、普通 return，以及保存和后续读取。回溯到父整体只解释来源，不扩大载荷。到外部边界停止，不猜接收方内部处理。

正式运行见 [联合分析链](joint-pipeline.md)，当前字段和保存说明见 [全流程收紧](../architecture/field-tightening.md)。[早期三例切片报告](../../experiments/doe/runs/slices-v1-20261010-165218/index.html) 是历史材料，其旧接口不作为当前入口。
