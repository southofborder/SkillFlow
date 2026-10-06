"""Construct the Data example offline; print a round-trippable registry as JSON.

Install the package first, then run this file. The IR and evidence locations below
are illustrative identifiers, not observations from a real Skill execution.
"""

from skillflow.propagation.data import Annotations
from skillflow.propagation.data import DataPart
from skillflow.propagation.data import DataReferenceError
from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import Dependency
from skillflow.propagation.data import FieldUpdatesContent
from skillflow.propagation.data import KnownPartsContent
from skillflow.propagation.data import LiteralContent
from skillflow.propagation.data import OpaqueContent
from skillflow.propagation.data import Origin
from skillflow.propagation.data import WholeExceptContent


def build_demo() -> DataRegistry:
    """Build source, composition, exclusion, overlay and dependency examples."""
    registry = DataRegistry("data-model-demo-v3")

    a = registry.register_source(
        "ir_read_profile/output/0",
        acquired_from="caller.profile",
        at="ir_read_profile",
        annotations=Annotations(description="调用者资料整体，尚未完整展开"),
    )
    owner = registry.register_part(
        a.id,
        ["owner"],
        annotations=Annotations(description="资料中的负责人信息"),
    )

    b = registry.register_source(
        "ir_read_document/output/0",
        acquired_from="expense_document",
        at="ir_read_document",
        annotations=Annotations(description="整份费用文档，不仅是已知字段"),
    )
    amount = registry.register_part(
        b.id,
        ["amount"],
        annotations=Annotations(description="文档中的金额数据"),
    )
    api_key = registry.register_part(
        b.id,
        ["api_key"],
        annotations=Annotations(
            description="凭据字段，只登记分析信息，不保存真实密钥",
        ),
    )
    # Describing these parts does not change B's identity or close its contents.
    assert registry.get(b.id).id == b.id
    assert registry.get(b.id).content.parts_complete is False
    assert registry.register_part(b.id, ["api_key"]).id == api_key.id

    total = registry.create_result(
        "ir_sum_amount/output/0",
        content=OpaqueContent(),
        origin=Origin(
            at="ir_sum_amount",
            inputs=[amount.id],
            dependencies=[Dependency(data=amount.id, relation="derived")],
        ),
        annotations=Annotations(description="金额合计；本例不实际执行求和"),
    )
    combined = registry.create_result(
        "ir_build_response/output/0",
        content=KnownPartsContent(
            parts=[
                DataPart(path=["owner"], data=owner.id),
                DataPart(path=["total"], data=total.id),
                DataPart(path=["debug"], data=b.id),
            ],
            parts_complete=True,
        ),
        origin=Origin(
            at="ir_build_response",
            inputs=[owner.id, total.id, b.id],
        ),
        annotations=Annotations(description="明确构造的 owner、total、debug 三部分"),
    )
    without_debug = registry.create_result(
        "ir_remove_debug/output/0",
        content=WholeExceptContent(base=combined.id, excluded_parts=[["debug"]]),
        origin=Origin(
            at="ir_remove_debug",
            inputs=[combined.id],
        ),
    )
    without_key = registry.create_result(
        "ir_remove_api_key/output/0",
        content=WholeExceptContent(base=b.id, excluded_parts=[["api_key"]]),
        origin=Origin(
            at="ir_remove_api_key",
            inputs=[b.id],
        ),
    )
    replacement = registry.create_result(
        "ir_replace_key/literal/0", content=LiteralContent(value="[redacted]"),
        origin=Origin(at="ir_replace_key"),
    )
    updated = registry.create_result(
        "ir_replace_key/output/0",
        content=FieldUpdatesContent(base=combined.id, updates=[
            DataPart(path=["debug", "api_key"], data=replacement.id),
        ]),
        origin=Origin(at="ir_replace_key", inputs=[combined.id, replacement.id]),
        annotations=Annotations(description="只覆盖一个字段，保留原整体的其余未知内容；不据此给出安全结论"),
    )
    updated_debug = registry.resolve_part(updated.id, ["debug"])
    assert isinstance(updated_debug.content, FieldUpdatesContent)
    assert updated_debug.content.base == b.id
    assert registry.resolve_part(updated_debug.id, ["api_key"]).id == replacement.id
    assert registry.get_part(b.id, ["api_key"]).id == api_key.id
    registry.create_result(
        "ir_complex_function/output/0",
        content=OpaqueContent(),
        origin=Origin(
            at="ir_complex_function",
            inputs=[owner.id, b.id],
            dependencies=[
                Dependency(data=owner.id, relation="possible"),
                Dependency(data=b.id, relation="possible"),
            ],
        ),
        annotations=Annotations(
            description="保留未排除的输入依赖，不声称输出包含整份输入明文",
        ),
    )

    # Later knowledge about B also applies to B's unexcluded remainder.
    address = registry.register_part(
        b.id,
        ["address"],
        annotations=Annotations(description="后来识别出的原有地址部分"),
    )
    assert registry.get_part(without_key.id, ["address"]).id == address.id
    assert registry.get_part(without_debug.id, ["total"]).id == total.id
    assert registry.get_part(combined.id, ["debug"]).id == b.id
    assert registry.get_part(b.id, ["api_key"]).id == api_key.id
    assert registry.resolve_part(updated_debug.id, ["address"]).id == address.id
    assert registry.resolve_part(updated.id, ["debug"]).id == updated_debug.id

    # Deterministic literal selection does not execute any Skill or function.
    literal = registry.create_result(
        "ir_literal/output/0", content=LiteralContent(value={"message": ["ok", None]}),
        origin=Origin(at="ir_literal"),
    )
    assert registry.resolve_part(literal.id, ["message", 1]).content.value is None

    # Querying an explicitly excluded part must never return its original data.
    try:
        registry.get_part(without_key.id, ["api_key"])
    except DataReferenceError:
        pass
    else:
        raise AssertionError("被明确排除的 api_key 不应重新出现")

    # Only this explicit, manually authored terminal annotation illustrates the
    # later DOE sensitivity stage. No propagation operation fabricates evidence.
    registry.refine(api_key.id, annotations=Annotations(
        sensitivity=["credential"],
        evidences=["人工敏感性示例：api_key 字段被定义为身份认证凭据；未保存真实密钥。"],
    ))
    registry.validate()
    restored = DataRegistry.from_json(registry.to_json())
    assert restored.to_dict() == registry.to_dict()
    return registry


if __name__ == "__main__":
    print(build_demo().to_json(indent=2))
