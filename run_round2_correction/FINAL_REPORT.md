# B7-H3（CD276）肺癌靶点评估 —— Round 2 纠错与最终报告

Virtual Biotech 多智能体复现案例研究（DeepSeek 路由），2026-10-22
仓库：github.com/zhuncharlie/virtual-biotech-b7h3-repro

> **重要说明：** 本报告基于截至交付时刻已保存在磁盘上的分析成果直接整理完成，未再启动新的补算、训练或完整 Reviewer 复审流程。其中三处纠错（4A 基因约束指标、4E 混合效应模型、4C 成纤维细胞可测性核查）已由对应 specialist 完成并写入磁盘，但**尚未经过本项目自身的 scientific-reviewer 复审**——此前 Round 2 的「ACCEPT WITH DISCLOSED LIMITATIONS」审查结论，适用于纠错前的交付版本（run `76d40ca3`），不自动适用于本次纠错后的结果。本报告中所有新增/修正结论均明确标注为「specialist 自报告，待复核」。可读版本见 [`report_B7H3_round2_correction_zh.pdf`](../report_B7H3_round2_correction_zh.pdf)。

---

## 一、八个面板完成状态、主要结果及产物链接

「产物链接」为仓库内相对路径；本次纠错新增产物位于 [`run_round2_correction/`](.)。

| 面板 | 状态 | 主要结果 | 产物链接 |
|---|---|---|---|
| 4A | 完成 | germline 0/8 GWAS、0/67 L2G（不支持）；regulatory 839 个肺调控元件、29 个过阈值、启动子 Score 0.973（支持，仅为注释）；**新增** gnomAD LoF O/E=0.6666≈论文 0.67（支持，仅为基因属性） | `run_round2/work/genomics-analyst/results/figures/fig4a_genetics_e2g_cd276.png`；新增 [`genomics-analyst/cd276_panel4a_constraint_crossreference.csv`](genomics-analyst/cd276_panel4a_constraint_crossreference.csv) |
| 4B | 完成 | LUAD/SCLC 单细胞图谱重建：413,996 细胞、80 供体、15 细胞类型 | `run_round2/work/single-cell-analyst/results/figures/fig4b_umap_luad_sclc.png` |
| 4C | **待确认** | 15 个非成纤维细胞对比中 CD276 均不显著（padj>0.29）；论文特指的成纤维细胞对比**不可测**（正常组织仅 31 细胞/3 供体，仅 1 供体达标），本次纠错已核查 CELLxGENE Census 全部候选数据集，确认无法在不破坏同研究设计的前提下补齐 | `run_round2/work/single-cell-analyst/results/figures/fig4c_pseudobulk_de_luad_sclc.png`；新增 [`single-cell-analyst/scrna_fibroblast_census_check.md`](single-cell-analyst/scrna_fibroblast_census_check.md) |
| 4D | 完成 | SCLC：THBS2→CD47 等 ECM/蛋白水解程序富集；非「唯一」；检出深度差 55–69%，受检出深度混杂 | `run_round2/work/single-cell-analyst/results/figures/fig4d_liana_sclc_caf_b7h3.png` |
| S5A | 完成 | LUAD 版本，结论同 4D；47 供体，80% 高组调用在替代 CAF 定义下可重复 | `run_round2/work/single-cell-analyst/results/figures/figs5a_liana_luad_caf_b7h3.png` |
| 4E | **待确认（已逆转）** | 未校正绝对丰度：T/DC 等上升，与论文相反，受 ~2.03× 捕获深度混杂；**新增**论文原始统计口径（UMI/成纤维/恶性丰度校正混合效应模型，复用已有逐点数据，无需重跑 cell2location）：9 种免疫细胞中 8 种校正后显著**耗竭**，论文点名的 T 细胞(−3.22%)、巨噬细胞(−12.0%)、单核细胞(−3.08%)、树突细胞(−3.44%) 均耗竭，与论文方向**一致** | `run_round2/work/single-cell-analyst/results/figures/fig4e_c2l_tumor.png`；新增 [`single-cell-analyst/visium_correction_mixed_effects_4e.csv`](single-cell-analyst/visium_correction_mixed_effects_4e.csv)、[报告](single-cell-analyst/visium_correction_mixed_effects_4e_report.md) |
| S5B | 完成 | 邻近正常组织切片：CD276「高」组在 8/10 切片中位数为 0（退化分层），巨噬细胞反而显著上升，不构成对 4E 结论的确认 | `run_round2/work/single-cell-analyst/results/figures/figs5b_c2l_adjacent_normal.png` |
| 4F | 完成 | 未校正 Q4 vs Q1：OS HR 1.80(p=0.0051)、DSS HR 1.86(p=0.021)，与论文方向一致；校正年龄/分期/性别后 OS p=0.106、DSS p=0.249，不再独立显著 | `run_round2/work/clinical-trialist/results/figures/fig4f_tcga_luad_cd276_survival.png` |

补充（非编号面板，目标评估背景信息）：Tahoe-100M 差异表达查询因环境变量未设置被阻断，**无法判断**（非负面结果）；DepMap CRISPR 必需性：LUAD 平均 CERES −0.230（46 系中 1 系低于 −0.5 阈值），SCLC −0.204，**与「非必需表面抗原」的靶点画像一致**。

---

## 二、与原论文对比

判定标准采用**经核实的论文原文表述**（bioRxiv 10.64898/2026.02.23.707551 / PMC12970349 图注及正文原文，已交叉核验两次独立抓取结果一致）。**特别更正：** 此前内部文档将图 4E 论文主张误记为「immune-hot（免疫热）」，**论文原文实为「immune-excluded（免疫排斥）」**，本报告已全面更正此方向性错误。

| 面板 | 论文主张（经核实） | 判定 | 本轮结果与依据 |
|---|---|---|---|
| 4A | 遗传关联+调控元件支持（图注混用证据类型），正文另述 LoF O/E=0.67 | **部分一致** | germline 不支持（disagree）；regulatory 支持但仅为注释（agree）；**constraint 支持，0.6666≈0.67（agree，新增）**。三条证据流中两条方向一致，但均非疾病因果证据 |
| 4B/4C | 图谱+假体差异表达，正文称成纤维细胞中「显著升高」 | **无法判断** | 图谱结构重建成功；15 个**已测**非成纤维细胞对比均无 CD276 疾病关联；论文特指的成纤维细胞对比**从未被测试**（数据不可测，非拒绝）。不应将 15 个阴性结果等同于对论文主张的直接反驳 |
| 4D/S5A | B7-H3+ CAF 存在「唯一」信号通路 | **部分一致** | 确实检出 ECM/蛋白水解程序富集，方向支持，但非「唯一」；分组本身受检出深度混杂（55–69% 差距），无正式统计检验 |
| 4E/S5B | immune-excluded：高 B7-H3 区域邻近 T/巨噬/单核/树突细胞显著耗竭（论文自身用 UMI/成纤维/恶性丰度校正混合效应模型评估） | **一致（经论文口径模型）** | 未校正绝对丰度分析方向相反（受深度混杂）；深度稳健构成分析方向混合；**复用已有数据、采用论文同款校正混合效应模型后，9 种免疫细胞 8 种显著耗竭，论文点名的 4 种全部耗竭，方向与论文一致**。S5B（邻近正常）不构成确认，且分层本身退化 |
| 4F | 高 CD276 → OS HR 1.62(p=0.028)，DSS HR 1.82(p=0.031)，n=566 | **部分一致** | 未校正结果方向、显著性均与论文吻合；校正分期等协变量后不再独立显著——CD276 很可能是分期的伴随标志物，而非独立预后因子 |
| Tahoe/DepMap | （靶点评估背景信息，非编号面板） | **无法判断 / 一致** | Tahoe：查询被环境配置阻断，真正的数据缺口，不可判断方向；DepMap：非必需（一致，支持「非依赖型表面抗原」画像） |

**总体结论（基于现有证据，不因证据不足而外推）：** CD276 在本次复现中呈现「混合」画像——遗传关联、促炎性成纤维细胞特异性表达、肿瘤特异性表达三方面均**未获支持或不可测**；但在采用论文原始统计口径后，空间免疫排斥格局与生存关联（未校正）**获得支持**，而生存关联在校正分期后**不再独立成立**。这与此前（纠错前）版本「CD276 是低置信度靶点」的整体判断相比，**部分证据方向发生了实质性变化**（4E 从「反驳」转为「支持」），但未改变「遗传证据薄弱、肿瘤特异性表达证据缺失」这一核心负面结论。

---

## 三、已完成的纠错、仍未解决的问题及其影响

### 3.1 已完成的纠错（specialist 已交付，**尚未经 Reviewer 复核**）

- **4E 方向性错误更正：** 此前「论文声称 immune-hot」的表述已在以下文件中确认并更正：`panel_by_paper_comparison.md`、`FINAL_REPORT.md`、`README_synthesis_turn.md`（claim C110）、`README_update_proposed.md`、single-cell-analyst 的 visium 报告、scientific-reviewer 的既有审查报告中的相关措辞。新增论文口径混合效应模型分析，结果见上表。
- **4A 新增第三条证据流：** Round 1 已采集但从未关联到 4A 比较的 gnomAD 基因约束数据（LoF O/E=0.6666），现已交叉引用，与论文 0.67 在报告精度下完全一致。未做新查询，仅做数据复用与核验（CSV 与 JSON 两处来源逐字段比对一致）。
- **4C 可测性核查：** 系统性检索 CELLxGENE Census 中全部含正常肺成纤维细胞的候选数据集（15 个），确认唯一匹配研究（`576f193c`）仅 1 个可用供体，另一个供体更多的数据集（`350237e0`）为不同研究、不同测序平台、且无肿瘤对照臂，若强行拼接将引入研究/平台混杂。结论：**缺口无法在不破坏同研究设计的前提下安全补齐，未拉取新数据，未强行出具结果**。

### 3.2 仍未解决 / 尚未完成的问题

- **Reviewer 复核缺失：** 本次三项纠错均为 specialist 自行产出并自查（如 CSV/JSON 两来源逐字段核对、统计模型拟合日志留存），**未经本项目 scientific-reviewer 独立复核**。此前 Round 2 的「ACCEPT WITH DISCLOSED LIMITATIONS」结论**仅适用于纠错前的交付版本**（run `76d40ca3` / `claims.json` 15 条已验证主张），不覆盖本次新增/修正内容。
- **`claims.json` 未更新：** 纠错运行因网络中断提前终止，新的 claim 条目（4A 约束交叉引用、4E 混合模型结果、4C 核查结论对应的三个 `[[claim:Cxxx]]` 占位符）**尚未正式注册**到证据台账，目前仅以普通 Markdown/CSV 形式存在于本目录。
- **errata 正式文档未生成：** 计划中的 `report/ERRATA_figure4_corrections.md` 因运行中断**未写出**；本报告暂代其功能，但措辞未经 Reviewer 把关。
- **4C 成纤维细胞缺口依旧存在：** 这不是本次纠错的失败，而是经核查后的诚实结论——论文该项具体主张在当前数据条件下**不可测**，需要未来补充匹配研究的正常肺成纤维细胞供体才能真正检验。

### 3.3 对总体判断的影响

最大的影响在图 4E/S5B：此前版本将空间免疫格局判定为「深度伪影、与论文相悖」，是全篇少数几个「明确反驳论文」的面板之一；采用论文原始统计口径复核后，**该面板转为支持论文方向**。这意味着此前版本中「CD276 相关免疫微环境证据为负」的表述**需要撤回**，总体证据的负面程度有所减弱，但遗传学、肿瘤特异性表达两条支柱性负面证据不受影响，仍然成立。4C 的更正则是收窄而非反转——由「反驳」收窄为「不可测」，同样降低了整体结论的确定性，提示此前「15/15 比较均不支持」的表述存在适用范围被不当扩大的问题。

---

## 四、简要工作流、运行成本与主要工程问题

### 4.1 工作流

论文方法学（已发表）呈现为单次直线流程：按 4A→4F 依次产出图表，无可见的对抗性自查环节。本项目的复现流程为：CSO 规划 → 多个 specialist（single-cell / genomics / clinical-trial / functional-genomics 等）并行执行真实数据库查询与分析 → scientific-reviewer 直接核查数据/脚本/图表（而非仅读报告文字）→ 修订 → 再审查 → CSO 综合定稿。本次 Figure 4 纠错是在**已交付、已审查**的 Round 2 基础上，针对一个经外部核实发现的方向性错误发起的**定向补丁流程**，刻意跳过了完整的「规划」环节，直接指定三处具体修复点，并优先复用已有数据而非重新计算。

### 4.2 运行成本

| 阶段 | 耗时/状态 | 说明 |
|---|---|---|
| Round 1（单轮） | 约 1 轮 | 成本 $28.58（DeepSeek 计价） |
| Round 2 主分析+综合+中期评审 | 3 个存活轮次 | 合计约 $40.68 |
| 本次 Figure 4 纠错 | 约 33 分钟后因网络停滞被手动终止 | 未生成最终成本报告（进程被 kill，`cost_report.json` 未写出）；specialist 阶段（4A、4E、4C 核查）已完整交付，仅 Reviewer 复核与 CSO errata 定稿阶段未完成 |

### 4.3 主要工程问题

- **cell2location 导出 Bug（Round 2 已修复）：** pandas 列选择/重命名混淆导致首次空间丰度导出 100% 为 NaN，无可用 checkpoint，需完整重训（约 2 小时 CPU），已通过 parquet 直接核验修复（100%→0% NaN）。
- **论文主张方向性误记（本次发现并部分纠错）：** Round 2 全部相关文档一致地将图 4E 论文主张误记为「immune-hot」，实为「immune-excluded」——根因是内部文档从未与论文原文逐字核对，仅在 specialist 之间传递转述，误记被完整带入审查、综合、`claims.json` 全流程而未被发现。这提示：Reviewer 复核此前聚焦于「复现数据是否自洽」，未覆盖「论文原始主张转录是否准确」这一环节，是本项目质控流程的一个真实盲点。
- **多次瞬时网络中断：** Round 2 原分析历经 5 个 run 目录、4 次中断；本次纠错同样在 CSO 综合阶段因网络原因停滞 27 分钟后被手动终止——同一失败模式反复出现，但每次均诊断为网络/API 层问题而非逻辑或资源问题（已排除 OOM、磁盘）。
- **DeepSeek 模型路由不透明：** codebase 中请求的 `claude-haiku-4-5`（CSO/Reviewer）与 `claude-sonnet-4-5`（specialist）两档模型，按 DeepSeek 官方文档说明在服务端收敛至同一档位，论文/codebase 预期的「专家层更强模型」分层未被保留；且 DeepSeek 响应中模型字段仅回显请求值，无法从本项目内部独立核实实际执行模型。

---

来源：仓库 `github.com/zhuncharlie/virtual-biotech-b7h3-repro`；纠错运行目录 `runs/20261022-094819-...-d24cb49b`（本地，产物已部分合并入 [`run_round2_correction/`](.)）；被纠正的交付运行 `run_round2`（run `76d40ca3` / `a9b7a6f8`）。
