"""
GNN/序列 探针 v2 (numpy / 随机未训练权重)
================================================
v1 的错误:判定对象是 node(584 个),一个节点只出一个分。
   但你的 necessity 判定单元是 (observation x label_flow) —— 同一个边界节点上
   平均流过 14.5 条 label_flow、3.9 种不同敏感度的 label。node 级一个分根本无法区分。

v2 的修正:判定对象 = label_flow。
   每条 label_flow 的输入 = [它路过的节点向量序列] + [它自己的 label 属性向量]。
   同一个节点上的不同 label_flow,节点向量相同,但 label 属性不同 -> 输出不同的分。
   这就是 v1 做不到、而 necessity 真正需要的"按 label 区分"。

本版仍是随机权重,分数无意义;目的是让你【亲眼看到】:
   同一个边界节点,不同 label -> 不同的输入向量 -> 不同的分数。

依赖:只用 numpy。
用法:python experiments/labelflow_probe.py <fcg.json>
"""
import sys, json, hashlib
import numpy as np

np.random.seed(0)
D_TEXT = 64
HIDDEN = 32

# label 属性的简单词表(把分类型属性编成 one-hot/数值)
SENS_RANK = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}


def encode_text(s):
    """占位文本编码(哈希),真正使用时换成冻结 sentence-transformers。"""
    s = (s or "").lower()
    vec = np.zeros(D_TEXT, dtype=np.float32)
    for t in s.replace("_", " ").replace(".", " ").split():
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        vec[h % D_TEXT] += 1.0
    n = np.linalg.norm(vec)
    return vec / n if n > 0 else vec


def encode_label(lab):
    """把一条 label_flow 自己的标签属性编成向量。
    这是 v2 的关键:同一节点上不同 label,靠这个向量区分开。
    用 category.subtype 的文本嵌入 + 敏感度数值 + field 文本嵌入。"""
    cat = encode_text(f"{lab.get('category','')} {lab.get('subtype','')}")
    fld = encode_text(f"{lab.get('field_name','')} {lab.get('field_path','')}")
    sens = np.array([SENS_RANK.get(lab.get("sensitivity", ""), 0.0)], dtype=np.float32)
    conf = np.array([float(lab.get("confidence", 0.0))], dtype=np.float32)
    return np.concatenate([cat, fld, sens, conf])      # 维度 = 64+64+1+1 = 130


def encode_all_nodes(fcg):
    """给每个节点算一个向量(共享'零件库')。
    这一版用文本占位嵌入;真正版本这里可以是冻结编码器,或浅 GNN 的输出。
    返回 id -> 向量。"""
    out = {}
    for n in fcg["nodes"]:
        text = " ".join([n.get("name", ""), n.get("semanticKind", ""),
                         n.get("instructionText", ""), n.get("description", "")])
        out[n["id"]] = encode_text(text)
    return out


def rebuild_seq(fl, by_id, limit=20):
    """用 parent_label_flow_id 链重建一条 label_flow 路过的节点 id 序列(origin->current)。"""
    seq, cur, guard, seen = [], fl, 0, set()
    while cur and guard < limit:
        seq.insert(0, cur.get("current_node"))
        p = cur.get("parent_label_flow_id")
        if not p or p in seen:
            break
        seen.add(p)
        cur = by_id.get(p)
        guard += 1
    return [nid for nid in seq if nid]


def build_unit_input(fl, by_id, node_vecs):
    """构造一条 label_flow 的判定输入向量。
    = 序列节点向量做平均池化(把变长序列压成定长) ++ 该 label 的属性向量。
    池化是把'路径'压成一个定长表示的最简做法;真正版本这里换成
    序列模型(Transformer/池化层),但形状与思路一致。"""
    seq = rebuild_seq(fl, by_id)
    if seq:
        mats = np.stack([node_vecs[nid] for nid in seq if nid in node_vecs])
        path_vec = mats.mean(axis=0)            # 平均池化 [D_TEXT]
    else:
        path_vec = np.zeros(D_TEXT, dtype=np.float32)
    lab_vec = encode_label(fl.get("label", {}))  # [130]
    return np.concatenate([path_vec, lab_vec]), len(seq)


def readout_head(x, Win):
    """读出头:输入向量 -> necessity 分 (0~1)。随机权重 -> 数值无意义。"""
    z = x @ Win
    return float(1.0 / (1.0 + np.exp(-z)))


def main():
    if len(sys.argv) < 2:
        print("用法: python experiments/labelflow_probe.py <fcg.json>")
        sys.exit(1)
    fcg = json.load(open(sys.argv[1], encoding="utf-8"))
    sp = fcg.get("security_profile", {})
    flows = sp.get("label_flows", [])
    obs = sp.get("observations", [])
    by_id = {fl["label_flow_id"]: fl for fl in flows}
    print(f"[load] {sys.argv[1]}")
    print(f"[data] {len(obs)} 个 observation, {len(flows)} 条 label_flow\n")

    node_vecs = encode_all_nodes(fcg)
    print(f"[节点零件库] 已给 {len(node_vecs)} 个节点各算一个 {D_TEXT} 维向量(共享)\n")

    Fin = D_TEXT + 130
    Win = np.random.randn(Fin, 1).astype(np.float32) * (1.0 / np.sqrt(Fin))

    target = None
    for o in obs:
        labs = set()
        for i in o.get("label_flow_ids", []):
            fl = by_id.get(i)
            if fl:
                l = fl.get("label", {})
                labs.add(f"{l.get('category')}.{l.get('subtype')}|{l.get('sensitivity')}")
        if len(labs) >= 5:
            target = o
            break
    if target is None:
        target = obs[0]

    print("=== 演示:同一个边界节点上的多条 label_flow 各自判定 ===")
    print(f"observation {target['observation_id']} @ 节点 {target.get('node_name')} "
          f"(边界={target.get('boundary',{}).get('trust_boundary')})\n")
    print(f"{'label_flow':>12} | {'label (category.subtype|sens)':<42} | {'路径长':>5} | {'necessity*':>10}")
    print("-" * 82)

    seen_labels, rows = set(), []
    for lfid in target.get("label_flow_ids", []):
        fl = by_id.get(lfid)
        if not fl:
            continue
        l = fl.get("label", {})
        key = f"{l.get('category')}.{l.get('subtype')}|{l.get('sensitivity')}"
        if key in seen_labels:
            continue
        seen_labels.add(key)
        x, slen = build_unit_input(fl, by_id, node_vecs)
        rows.append((lfid, key, slen, readout_head(x, Win), x))
        if len(rows) >= 8:
            break

    for lfid, key, slen, score, _ in rows:
        print(f"{lfid:>12} | {key:<42} | {slen:>5} | {score:>10.3f}")

    print("\n[关键验证] 同一个节点,不同 label 的【输入向量】是否真的不同?")
    for b in range(1, len(rows)):
        d = np.linalg.norm(rows[0][4] - rows[b][4])
        tag = "不同(可区分)" if d > 1e-6 else "相同(无法区分!)"
        print(f"   {rows[0][0]} vs {rows[b][0]}: 向量距离={d:.3f}  -> {tag}")

    print("\n=== 结论 ===")
    print("v1(node级):这个节点只得到 1 个向量、1 个分 —— 上面这些不同 label 被迫共享一个分。")
    print("v2(label_flow级):每条 label_flow = [路径节点向量池化] + [自己的label属性] -> 各自一个分。")
    print("'向量距离>0'证明:同节点不同 label 现在能被区分。这才匹配 (obs x label_flow) 判定粒度。")
    print("\n注:随机权重,分数无意义;有意义需先有标签再训练,并把池化换成真正的序列模型。")


if __name__ == "__main__":
    main()
