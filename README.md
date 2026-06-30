# Moi Hardware Inquiry Skill · 硬件设备询价与报价比对

![License](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)
![Skill](https://img.shields.io/badge/Skill-Agent-111111?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Supported-6B5B95?style=flat-square)

一个适配 Claude Code 等 Agent 环境的硬件询价技能，用于从招标技术文件（docx/xlsx）中**自动提取硬件设备需求、生成询价指引、比对厂商报价、审核采购合同**。

核心流程：解析技术文件 → 自动分类（硬件/软件/服务）→ 生成询价指引（厂商/型号/参考价格）→ 导入厂商报价逐项比对 → 生成参数偏离表 → 多厂商横向对比 / 合同审核。

> 由 [MoiTempete](https://github.com/MoiTempete) 基于真实煤矿网络安全、云计算中心等多个项目的硬件采购实践沉淀而成。

## 30 秒开始

```bash
git clone https://github.com/MoiTempete/moi-hardware-inquiry ~/.claude/skills/moi-hardware-inquiry
```

也可以直接把这段话发给有 shell 权限的 AI Agent：

```text
帮我安装 moi-hardware-inquiry skill。请把 https://github.com/MoiTempete/moi-hardware-inquiry 克隆到 ~/.claude/skills/moi-hardware-inquiry，安装完成后检查 SKILL.md、references/、scripts/ 是否存在。
```

安装后直接对 Agent 说：

```text
帮我分析这份招标文件里的硬件设备需求，做个询价指引。
```

也可以试这些请求：

```text
这份设备清单里有哪些是硬件哪些是软件授权？帮我分类并生成询价单。
收到了三家厂商报价，帮我逐一比对招标要求，生成偏离表。
这是拟签的采购合同，帮我对照招标要求审核一下硬件配置是否合规。
```

## 效果

- 📋 **多格式解析**：支持 docx 技术规格书（段落提取 + 表格解析）和 xlsx 设备清单，从混排清单中自动区分硬件设备、软件授权、服务
- 🏷 **自动分类标注**：按关键词分类为硬件/软件/服务，识别强制项（★/不低于/必须）、配置自设计项、待澄清项
- 💰 **两种询价输出**：内部询价建议文档（含价格区间+置信度+策略建议）+ 外部脱敏分项询价单（按供应商类型分 Sheet，供应商直接填写）
- 🔍 **智能参数比对**：自动提取 CPU/内存/吞吐量/端口/并发连接等关键参数，逐项判定 ✅满足 / 🔺正偏离 / 🔻负偏离 / ⚠无法判断
- 📊 **三种比对模式**：纯询价模式 → 报价比对模式 → 合同比对模式，覆盖从招标分析到签约审核的全链路
- 🆚 **多厂商横向对比**：同框展示各厂商的型号/参数/价格/判定，自动推荐最优选择
- 📄 **合同审核**：检查采购合同 vs 招标要求的缺失项、范围外项、质保条款、配件来源
- 📚 **内置参考库**：30+ 条实战验证的设备价格和技术参数，既可做价格锚点也可做参数合理性判断基准

## 适合 / 不适合

**✅ 合适**：信息化平台、网络安全、云计算中心、工控系统等技术型招标中的硬件设备询价和核价场景。设备清单与软件授权混排、厂商报价格式不一致、合同范围与招标要求有偏差的复杂场景尤其适用。

**❌ 不合适**：纯软件采购（不含硬件）、纯服务采购（不含设备）、日常办公用品采购（走集采即可）、单品类单价询价（如只买一种标准品）。

## 常见使用场景

| 任务 | 推荐方式 |
|------|---------|
| 刚拿到招标文件，不知道预算 | 纯询价模式：Step 1 解析 → Step 2 生成询价指引 + 脱敏询价单 |
| 收到 1 家厂商报价，要核参数 | 报价比对模式：Step 3 单厂商偏离表 |
| 收到 2+ 家厂商报价，要选型 | 报价比对模式：Step 3 → Step 4 多厂商横向对比 |
| 拿到拟签合同，要审核 | 合同比对模式：Step 4 合同 vs 招标逐项比对 + 缺失项清单 |
| 招标要求中有"配置自设计" | Step 1.5 方案确认 → 三档方案梯度（经济/推荐/高性能）|
| 设备清单混有 Oracle/虚拟化等软件授权 | Step 1 自动分类 → 硬件与软件分开列表、分开询价 |

## 为什么是 Agent Skill

- **招标文件格式多变**：docx 中的段落描述和嵌套表格、xlsx 中的合并单元格和空白行——Agent 的理解能力比正则脚本更灵活
- **分类需要语义判断**："终端威胁检测与响应"是硬件还是软件？Agent 能根据上下文判断
- **参数比对不是简单的数字大小**：CPU 主频低 4% 但核心数多 33% 综合更强——需要综合判断而非机械比对
- **合同审核需要全局视角**：合同包含了通信网络但漏了 FC 交换机——Agent 能从技术架构层面发现这种系统性风险
- **三种模式灵活切换**：用户可能跳过询价直接比报价、跳过报价直接审合同，Agent 按需调整流程

## 安装

### 方式一：命令行安装（推荐）

```bash
git clone https://github.com/MoiTempete/moi-hardware-inquiry ~/.claude/skills/moi-hardware-inquiry
```

### 方式二：把下面这段话直接发给 AI

> 帮我安装 `moi-hardware-inquiry` 这个 Claude Code skill。请按下面步骤做：
>
> 1. 确保 `~/.claude/skills/` 目录存在（不存在就创建）
> 2. 执行 `git clone https://github.com/MoiTempete/moi-hardware-inquiry.git ~/.claude/skills/moi-hardware-inquiry`
> 3. 验证：`ls ~/.claude/skills/moi-hardware-inquiry/` 应该看到 `SKILL.md`、`references/`、`scripts/` 三项
> 4. 告诉我安装好了，之后我说"硬件询价"之类的话就会触发这个 skill

### 方式三：通过 moi-bid-response 自动引导

如果已安装 `moi-bid-response`，在技术响应文件中遇到硬件设备需求时，Agent 会建议启动 `moi-hardware-inquiry` 进行询价分析。

### 触发方式

装好后，Claude Code 会在对话里自动发现并调用这个 skill。触发关键词：

- "帮我分析硬件设备需求"
- "生成询价指引"
- "比对厂商报价"
- "核对报价参数"
- "审核采购合同"
- "硬件询价"
- "设备偏离表"
- "hardware inquiry"

## 使用流程

Skill 本身是结构化工作流，Agent 会逐步引导：

1. **解析硬件需求** — 运行 `parse_hardware.py` 提取设备清单，自动分类硬件/软件/服务
2. **方案确认**（如需）— "配置自设计"设备先定硬件方案再询价
3. **生成询价指引** — 内置参考库 + LLM 估算，输出内部建议文档 + 外部脱敏询价单
4. **报价比对** — 导入厂商报价，逐项比对参数，生成偏离表
5. **多厂商对比 / 合同审核** — 横向选型推荐 或 合同缺失项 + 风险分析

详细说明见 [`SKILL.md`](./SKILL.md)。

## 三种比对模式

| 模式 | 输入 | 触发条件 | 核心输出 |
|------|------|---------|------|
| **纯询价** | 仅招标需求 | 用户只有技术文件，无厂商反馈 | 询价建议 xlsx + 脱敏分项询价单（Step 2） |
| **报价比对** | 招标需求 + 1-N 家厂商报价 | 用户收到厂商报价 | 单厂商偏离表 + 多厂商对比报告（Step 3-4） |
| **合同比对** | 招标需求 + 采购合同 | 用户拿到拟签合同 | 合同偏离表 + 缺失项清单 + 签约前建议（Step 4） |

## 偏离判定体系

| 判定 | 含义 | 示例 |
|:---:|------|------|
| ✅ **满足** | 参数等于或优于要求，在合理范围内 | 要求 64GB 内存，报价 64GB |
| 🔺 **正偏离** | 参数显著优于要求（可能过度采购或浪费预算） | 要求千兆防火墙，报价 220G 核心级防火墙 |
| 🔻 **负偏离** | 参数不满足要求（投标无效风险） | 要求吞吐 ≥20Gbps，报价 3Gbps SD-WAN |
| ⚠️ **无法判断** | 报价单未提供该参数，需向厂商确认 | 未标注内存规格 |
| ❌ **缺失** | 合同比对模式特有——合同未包含招标要求的设备项 | 合同有 FC HBA 卡但无 FC 交换机 |

## 核心编写原则

1. **先分类再询价**：硬件、软件授权、服务分开处理，避免把 Oracle 许可当硬件询价
2. **配置自设计设备先定方案**：未经确认的硬件方案价格跨度可达 5-10 倍，先给三档梯度让用户选择
3. **置信度透明**：每项价格建议标注置信度（🟢内置库/🟡LLM估算/🔴需确认），用户一眼知道可信度
4. **负偏离高亮警告**：不达标项必须醒目标注——这是投标无效的直接风险
5. **正偏离提醒成本**：参数超标不等于好事，同时标注额外成本帮助用户判断是否必要
6. **无法判断 ≠ 满足**：报价单缺失的参数不能默认为合规
7. **外部询价单必须脱敏**：从 docx 招标文件提取的参数，发给供应商前删除项目名称/甲方/招标编号
8. **内置库双向查询**：equipment-db 既是价格参考也是技术参数基准，用于判断报价配置合理性

## 目录结构

```
moi-hardware-inquiry/
├── SKILL.md                         ← Skill 主文件：工作流、关键规则、三种比对模式
├── README.md                        ← 本文件
├── CONTRIBUTING.md                  ← 贡献指南
├── LICENSE                          ← AGPL-3.0
├── .github/
│   ├── pull_request_template.md
│   └── ISSUE_TEMPLATE/
│       ├── config.yml
│       ├── bug_report.yml
│       └── feature_request.yml
├── scripts/
│   ├── parse_hardware.py            ← 硬件需求解析脚本（xlsx/docx → 结构化JSON）
│   └── compare_quotation.py        ← 报价比对脚本（需求JSON + 报价xlsx → 偏离表JSON）
└── references/
    └── equipment-db.md             ← 内置设备参考库（价格基准 + 技术参数基准）
```

## Roadmap

- 报价单 OCR / PDF 解析支持
- 更多设备品类的参考库扩展（工控设备、机房基础设施等）
- 基于历史比价数据的自动预算建议
- Web UI 模式：上传文件 → 自动生成对比报告下载
- 集成招投标平台的公开中标价数据

## FAQ

**和 moi-bid-response 是什么关系？**
`moi-bid-response` 生成技术响应文件（docx），其中可能包含硬件设备配置方案。`moi-hardware-inquiry` 负责将这些硬件需求落实为具体的询价、核价和合同审核。两者可独立使用，也可串联。

**和 moi-bid-defense 是什么关系？**
`moi-bid-defense` 将技术响应转化为讲标幻灯片。`moi-hardware-inquiry` 专注硬件采购环节。三个 skill 覆盖投标全链路：写标书 → 核硬件 → 讲标。

**内置参考库的价格准吗？**
参考库标注了来源（实战-素材X）和日期，反映特定项目的成交价或报价。不同项目的批量、定制需求、付款条件会导致价格差异。使用时作为锚点参考，实际询价以厂商书面报价为准。

**支持哪些设备品类？**
当前参考库覆盖网络安全设备（防火墙/网闸/态势感知/堡垒机/日志审计/数据库审计）、服务器（通用/GPU/AI推理）、存储（分布式/双活/备份）、网络设备（交换机）、终端与外设、软件授权。工控设备、机房基础设施等品类待扩展。

**怎么更新到最新版？**
在本地 skill 目录执行 `git pull`。

## 贡献

Bug、提取质量问题、新的设备品类需求——欢迎开 Issue 或 PR。改动请优先：

- 在 `references/equipment-db.md` 中补充新的设备型号和价格
- 在 `scripts/parse_hardware.py` 中优化分类关键词和提取规则
- 在 `scripts/compare_quotation.py` 中优化参数比对逻辑
- 工作流改动不能移除用户确认闸门（Step 1 / Step 2 / 逐厂商比对）

详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

## 关联 Skills

### 上游 — 技术响应文件生成

**[`moi-bid-response`](https://github.com/MoiTempete/moi-bid-response)** — 从招标技术规格书自动编写投标技术响应文件。响应文件中的硬件配置方案可作为 `moi-hardware-inquiry` 的输入。

```bash
npx skills add https://github.com/MoiTempete/moi-bid-response --skill moi-bid-response
```

### 下游 — 讲标答辩幻灯片

**[`moi-bid-defense`](https://github.com/MoiTempete/moi-bid-defense)** — 从技术响应文件中自动提取差异化亮点，生成讲标幻灯片。

```bash
git clone https://github.com/MoiTempete/moi-bid-defense ~/.claude/skills/moi-bid-defense
```

**完整链路**：招标文件 (.docx) → `moi-bid-response` → 技术响应 (.docx/.md) → `moi-hardware-inquiry`（硬件询价+核价）+ `moi-bid-defense`（讲标PPT）

## 更新日志

### 2026-06-30

**SKILL.md 三轮实战验证完成**

- Step 2 输出重构为双轨制：内部询价建议文档（4 Sheet）+ 外部脱敏分项询价单（按供应商类型分 Sheet）
- 新增「自动分类」章节：硬件/软件/服务分类关键词表 + 混排清单处理规则
- 新增「配置自设计设备的处理」：方案确认子步骤（Step 1.5）+ 三档方案梯度
- 新增 Step 4「多厂商对比与合同比对」+ 三种比对模式总结
- Step 3 匹配逻辑区分情况一（同格式行对行）和情况二（自由格式模糊匹配）
- 关键规则从 8 条扩展至 13 条
- 实战沉淀 8 条关键发现写入验证记录

**scripts/parse_hardware.py**

- 支持 xlsx 设备清单自动分类（硬件/软件/服务）、强制项检测、配置自设计标记、待澄清标记
- 支持 docx 技术规格书的段落和表格提取，供 LLM 辅助分析
- 输出标准化 JSON

**scripts/compare_quotation.py**

- 需求 JSON × 报价 xlsx → 偏离表 JSON
- 自动提取并比对 CPU 核数/内存容量/吞吐量/端口数/并发连接数等关键参数
- 两阶段匹配：精确名称 → 关键词重叠度
- 判定：meet / positive_deviation / negative_deviation / unclear

**references/equipment-db.md**

- 30+ 条实战验证设备价格和技术参数
- 覆盖网络安全/服务器/存储/网络设备/软件授权/终端外设 6 大品类
- 双重用途：价格基准 + 技术参数合理性判断基准

### 2026-06-29

- 初始 SKILL.md 框架设计
- 三步骤工作流：解析需求 → 生成询价指引 → 比对报价
- 七类设备分类体系 + 四种偏离判定

## License

AGPL-3.0 © 2026 [MoiTempete](https://github.com/MoiTempete)
