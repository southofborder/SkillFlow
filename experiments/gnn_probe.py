"""
GNN 探针 (第一版 / numpy / 随机未训练权重)
================================================
目的:在真实的 skill fcg.json 上,亲眼看到一条完整管线跑通——
   构图 -> 节点特征 -> 5 层消息传递(+JK-Net) -> 读出头 -> 每个边界节点一个 necessity 分。

重要前提(务必记住):
   本版权重全是【随机未训练】的,所以输出的向量和分数【没有任何意义】。
   这一版只验证:形状对不对、信息在图上是否真的逐层传播、管线是否通。
   真要有意义的 necessity,需要先有标签(teacher 蒸馏/可证明/注入)再训练。

依赖:只用 numpy(已装)。文本编码用的是【哈希占位】,不是真语义编码器;
   真正上场时这一步换成冻结的 sentence-transformers(见 encode_text 注释)。

用法:
   python experiments/gnn_probe.py <fcg.json 路径>
"""
import sys, json, hashlib
import numpy as np

np.random.seed(0)               # 固定随机种子,方便复现
D_TEXT = 64                     # 文本占位嵌入维度
HIDDEN = 32                     # 每层 GNN 的隐藏维度
NUM_LAYERS = 5                  # 你要的 5 层(感受野 = 5 跳)


def encode_text(s):
    """占位文本编码:把字符串哈希成定长向量。
    这【不是】真语义编码——意思相近的词不会得到相近向量。
    真正使用时,把这个函数替换成冻结的 sentence-transformers:
        model = SentenceTransformer('all-MiniLM-L6-v2')  # 加载一次
        return model.encode(s)                            # 每个节点跑一次
    现在用哈希只是为了无依赖、能立刻跑起来看管线。"""
    s = (s or "").lower()
    vec = np.zeros(D_TEXT, dtype=np.float32)
    toks = s.replace("_", " ").replace(".", " ").split()
    for t in toks:
        h = int(hashlib.md5(t.encode()).hexdigest(), 16)
        vec[h % D_TEXT] += 1.0
    n = np.linalg.norm(vec)
    return vec / n if n > 0 else vec


def build_graph(fcg):
    """从 fcg.json 构图。返回:
       node_ids        : 节点 id 列表(行号 = 矩阵下标)
       X               : [N, F] 初始节点特征矩阵
       adj             : [N, N] 归一化邻接(含自环),消息传递用
       sink_idx        : 边界(Sink)节点的下标列表
       id2row          : id -> 行号
    """
    nodes = fcg["nodes"]
    node_ids = [n["id"] for n in nodes]
    id2row = {nid: i for i, nid in enumerate(node_ids)}
    N = len(nodes)

    # --- 节点特征 = 文本占位嵌入 + 几个结构 one-hot ---
    CATS = ["Source", "Intermediate", "Sink"]
    feats = []
    for n in nodes:
        text = " ".join([n.get("name", ""), n.get("semanticKind", ""),
                         n.get("instructionText", ""), n.get("description", "")])
        t = encode_text(text)
        cat = np.array([1.0 if n.get("category") == c else 0.0 for c in CATS], dtype=np.float32)
        crit = np.array([1.0 if n.get("is_critical") else 0.0], dtype=np.float32)
        feats.append(np.concatenate([t, cat, crit]))
    X = np.stack(feats).astype(np.float32)            # [N, D_TEXT+4]

    # --- 邻接:用 data_dependency + doc_instruction 边(数据真正流过的边) ---
    A = np.zeros((N, N), dtype=np.float32)
    kept = 0
    for e in fcg["edges"]:
        if e["type"] not in ("data_dependency", "doc_instruction"):
            continue
        s, t = e.get("source"), e.get("target")
        if s in id2row and t in id2row:
            A[id2row[t], id2row[s]] = 1.0             # 让 target 能"看到" source(信息逆数据流方向聚合到下游边界)
            kept += 1
    A += np.eye(N, dtype=np.float32)                  # 自环:每个节点也保留自己

    # --- 对称归一化 D^-1/2 (A) D^-1/2,防止度大的节点数值爆炸(GCN 标准做法) ---
    deg = A.sum(axis=1)
    dinv = np.where(deg > 0, deg ** -0.5, 0.0)
    adj = (dinv[:, None] * A) * dinv[None, :]

    sink_idx = [i for i, n in enumerate(nodes) if n.get("category") == "Sink"]
    print(f"[graph] N={N} 节点, 用了 {kept} 条数据流边, Sink(边界)={len(sink_idx)} 个, 特征维度={X.shape[1]}")
    return node_ids, X, adj, sink_idx, id2row


def relu(x):
    return np.maximum(0.0, x)


def message_passing(X, adj):
    """5 层消息传递。每层:聚合邻居 -> 线性变换 -> ReLU。
    返回每一层的输出 [H0, H1, ..., H5],H0 是输入投影后的初始表示。
    随机权重,仅看形状与传播。"""
    F_in = X.shape[1]
    # 先把原始特征投影到 HIDDEN 维(L0)
    W0 = np.random.randn(F_in, HIDDEN).astype(np.float32) * (1.0 / np.sqrt(F_in))
    H = relu(X @ W0)
    layers = [H]
    for layer in range(NUM_LAYERS):
        Wl = np.random.randn(HIDDEN, HIDDEN).astype(np.float32) * (1.0 / np.sqrt(HIDDEN))
        agg = adj @ H            # ← 这一行就是"每个节点把邻居的向量加权求和" = 消息传递
        H = relu(agg @ Wl)
        layers.append(H)
        print(f"[layer {layer+1}] 完成第 {layer+1} 轮消息传递 -> 感受野 {layer+1} 跳, H 形状 {H.shape}")
    return layers


def jk_concat(layers):
    """JK-Net (concat 版):把每一层的表示【拼起来】交给读出头,
    让读出头自己决定每个节点用浅层还是深层的信息。
    这就是'每个节点各选自己合适深度'的实现方式之一。"""
    return np.concatenate(layers, axis=1)             # [N, HIDDEN*(NUM_LAYERS+1)]


def readout_head(emb):
    """读出头:节点向量 -> 一个 0~1 的 necessity 分。
    一层线性 + sigmoid。随机权重 -> 分数无意义,只验证'向量能变成分数'。"""
    Fin = emb.shape[1]
    W = np.random.randn(Fin, 1).astype(np.float32) * (1.0 / np.sqrt(Fin))
    z = emb @ W
    return 1.0 / (1.0 + np.exp(-z)).reshape(-1)       # sigmoid -> [N]


def main():
    if len(sys.argv) < 2:
        print("用法: python experiments/gnn_probe.py <fcg.json>")
        sys.exit(1)
    fcg = json.load(open(sys.argv[1], encoding="utf-8"))
    print(f"[load] {sys.argv[1]}\n")

    node_ids, X, adj, sink_idx, id2row = build_graph(fcg)
    print()
    layers = message_passing(X, adj)
    emb = jk_concat(layers)
    print(f"\n[jk-net] 拼接 {len(layers)} 层表示 -> 每节点维度 {emb.shape[1]}")
    scores = readout_head(emb)
    print(f"[readout] 得到每个节点的 necessity 分 (0~1) —— 注意:随机权重,数值无意义\n")

    # --- 看一眼某个边界节点在每一层之后'吸收'了多少信息(用向量的变化量衡量) ---
    if sink_idx:
        probe = sink_idx[0]
        print(f"[追踪] 边界节点 row={probe} id={node_ids[probe]} name={fcg['nodes'][probe].get('name')}")
        prev = layers[0][probe]
        for L in range(1, len(layers)):
            cur = layers[L][probe]
            delta = np.linalg.norm(cur - prev)
            print(f"   第 {L} 层后,该节点向量相对上一层变化量 = {delta:.3f}  (非0 => 又吸收了第 {L} 跳邻居的信息)")
            prev = cur
        print(f"\n[示例分数] 前 5 个边界节点的 necessity 分(无意义,仅看形状):")
        for i in sink_idx[:5]:
            print(f"   {node_ids[i]:>10}  {fcg['nodes'][i].get('name','')[:40]:<40}  score={scores[i]:.3f}")

    print("\n=== 管线跑通 ===")
    print("证明了:fcg.json -> 图 -> 节点特征 -> 5层消息传递 -> JK-Net 拼接 -> 读出头 -> 每节点一个分数。")
    print("下一步要让分数有意义:① encode_text 换成冻结 sentence-transformers ② 准备标签 ③ 用 torch/PyG 训练读出头+GNN。")


if __name__ == "__main__":
    main()
