# 🧬 BioAI-Lab

**AI for Synthetic Biology & Genomic Analysis**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Biopython](https://img.shields.io/badge/Biopython-1.82+-yellow?style=flat-square)](https://biopython.org)

合成生物学 AI 研究，用人工智能推动生命科学

</div>

---

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [核心模块](#核心模块)
- [使用教程](#使用教程)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## ✨ 功能特性

### 🧬 DNA序列设计
- **密码子优化**：针对特定宿主优化基因表达
- **GC含量控制**：优化序列稳定性和表达效率
- **酶切位点管理**：自动添加/移除限制性内切酶位点

### 🧪 序列分析
- **ORF识别**：自动查找开放阅读框
- **蛋白质翻译**：支持标准及替代遗传密码
- **序列统计**：GC含量、分子量、熔解温度

### 🎨 可视化
- **序列图谱**：DNA序列可视化
- **蛋白质结构**：3D结构展示
- **数据分析图表**：统计结果可视化

### 🤖 AI辅助设计
- **基因回路设计**：合成生物学回路构建
- **启动子优化**：转录效率预测
- **蛋白质预测**：AlphaFold结构预测集成

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/ENDcodeworld/BioAI-Lab.git
cd BioAI-Lab

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 快速测试

```bash
# 测试DNA序列分析
python src/sequence_analysis.py

# 测试密码子优化
python src/ai/codon_optimizer.py

# 测试DNA设计引擎
python src/core/dna_engine.py
```

---

## 📦 核心模块

### 1. DNA序列分析

```python
from src.sequence_analysis import SequenceAnalyzer

analyzer = SequenceAnalyzer()

# 示例：GFP基因序列
dna_sequence = """
ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGAT
GTTAATGGGCACAAATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTT
ACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCAACACTTGTCACTACT
""".replace('\n', '').replace(' ', '')

# 全面分析
results = analyzer.analyze(dna_sequence)

print("=" * 60)
print("📊 DNA序列分析报告")
print("=" * 60)
print(f"序列长度: {results['length']} bp")
print(f"GC含量: {results['gc_content']*100:.2f}%")
print(f"分子量: {results['molecular_weight']/1000:.2f} kDa")
print(f"熔解温度: {results['melting_temp']:.1f}°C")
print(f"序列复杂度: {results['complexity']*100:.1f}%")

# 核苷酸统计
print(f"\n核苷酸组成:")
for base, count in results['nucleotide_counts'].items():
    pct = count / results['length'] * 100
    print(f"  {base}: {count} ({pct:.1f}%)")

# 开放阅读框
print(f"\n开放阅读框 (ORF):")
for i, orf in enumerate(results['orf_info'][:3], 1):
    print(f"  ORF {i}: 位置 {orf['start']}-{orf['end']}, "
          f"长度 {orf['length_aa']} 氨基酸")

# 蛋白质翻译
protein = analyzer.translate(dna_sequence[:150])
print(f"\n蛋白质序列 (前50 AA): {protein}")
```

### 2. 密码子优化

```python
from src.ai.codon_optimizer import CodonOptimizer, OptimizationConfig
from src.core.dna_engine import HostOrganism

# 配置优化参数
config = OptimizationConfig(
    population_size=100,
    generations=50,
    target_gc=0.5,          # 目标GC含量 50%
    target_cai=0.9,         # 目标CAI
    mutation_rate=0.1
)

# 创建优化器
optimizer = CodonOptimizer(
    host=HostOrganism.E_COLI,  # 大肠杆菌表达
    config=config
)

# 蛋白质序列
protein_seq = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTT"

# 运行优化
result = optimizer.optimize(protein_seq)

print("=" * 60)
print("🧬 密码子优化结果")
print("=" * 60)
print(f"原始序列长度: {len(protein_seq) * 3} bp")
print(f"优化后序列长度: {len(result.optimized_dna)} bp")
print(f"GC含量: {result.gc_content*100:.2f}%")
print(f"CAI指数: {result.cai:.3f}")
print(f"优化得分: {result.score:.3f}")

# 显示优化后的序列
print(f"\n优化后的DNA序列:")
print(f"{result.optimized_dna[:60]}...")
```

### 3. DNA设计引擎

```python
from src.core.dna_engine import DNAEngine, HostOrganism, DesignConstraints

# 创建设计引擎
engine = DNAEngine(host=HostOrganism.E_COLI)

# 设计约束
constraints = DesignConstraints(
    avoid_restriction_sites=['EcoRI', 'BamHI'],
    min_gc=0.4,
    max_gc=0.6,
    avoid_repeats=True
)

# 设计基因序列
protein = "MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKSLHTLFGDKLCTVATLRETYGEMADCCAKQEPERNECFLQHKDDNPNLPRLVRPEVDVMCTAFHDNEETFLKKYLYEIARRHPYFYAPELLFFAKRYKAAFTECCQAADKAACLLPKLDELRDEGKASSAKQRLKCASLQKFGERAFKAWAVARLSQRFPKAEFAEVSKLVTDLTKVHTECCHGDLLECADDRADLAKYICENQDSISSKLKECCEKPLLEKSHCIAEVENDEMPADLPSLAADFVESKDVCKNYAEAKDVFLGMFLYEYARRHPDYSVVLLLRLAKTYETTLEKCCAAADPHECYAKVFDEFKPLVEEPQNLIKQNCELFEQLGEYKFQNALLVRYTKKVPQVSTPTLVEVSRNLGKVGSKCCKHPEAKRMPCAEDYLSVVLNQLCVLHEKTPVSDRVTKCCTESLVNRRPCFSALEVDETYVPKEFNAETFTFHADICTLSEKERQIKKQTALVELVKHKPKATKEQLKAVMDDFAAFVEKCCKADDKETCFAEEGKKLVAASQAALGL"

result = engine.design_dna(
    protein_sequence=protein,
    constraints=constraints
)

print(f"设计完成!")
print(f"序列长度: {result.length} bp")
print(f"GC含量: {result.gc_content*100:.2f}%")
print(f"CAI: {result.cai:.3f}")
print(f"得分: {result.score:.3f}")

if result.violations:
    print(f"\n警告: {len(result.violations)} 个约束违反")
    for v in result.violations:
        print(f"  - {v}")
```

---

## 📚 使用教程

### 教程1：表达载体设计

```python
"""
完整教程：为大肠杆菌设计表达载体
"""
from src.core.dna_engine import DNAEngine, HostOrganism
from src.ai.codon_optimizer import CodonOptimizer

# 1. 目标蛋白序列（示例：胰岛素）
insulin = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT"

# 2. 密码子优化
optimizer = CodonOptimizer(host=HostOrganism.E_COLI)
opt_result = optimizer.optimize(insulin)

print(f"优化后序列: {opt_result.optimized_dna[:50]}...")

# 3. 添加表达元件
# 启动子 + RBS + 优化序列 + 终止子
promoter = "TTGACA" + "TATAAT"  # 简单启动子示例
rbs = "AGGAGG"  # 核糖体结合位点
terminator = "TAA" + "GCCTAGCAT"

expression_cassette = promoter + rbs + opt_result.optimized_dna + terminator

print(f"\n表达盒长度: {len(expression_cassette)} bp")
print(f"预测表达水平: 高 (CAI={opt_result.cai:.2f})")
```

### 教程2：序列质量分析

```python
"""
序列质量检查教程
"""
from src.sequence_analysis import SequenceAnalyzer

analyzer = SequenceAnalyzer()

# 检查序列质量
def check_sequence_quality(dna_seq):
    results = analyzer.analyze(dna_seq)
    
    quality_score = 100
    issues = []
    
    # 检查GC含量
    gc = results['gc_content']
    if gc < 0.3 or gc > 0.7:
        quality_score -= 20
        issues.append(f"GC含量异常 ({gc*100:.1f}%)")
    
    # 检查复杂度
    if results['complexity'] < 0.5:
        quality_score -= 15
        issues.append("序列复杂度低")
    
    # 检查重复序列
    if results['repeats']:
        quality_score -= len(results['repeats']) * 5
        issues.append(f"发现 {len(results['repeats'])} 个重复序列")
    
    return quality_score, issues

# 测试
test_seq = "ATG" + "GC" * 100 + "TAA"
score, issues = check_sequence_quality(test_seq)

print(f"序列质量得分: {score}/100")
if issues:
    print("问题:")
    for issue in issues:
        print(f"  - {issue}")
```

---

## 🏗️ 项目结构

```
BioAI-Lab/
├── src/
│   ├── core/
│   │   └── dna_engine.py         # DNA设计引擎
│   ├── ai/
│   │   ├── codon_optimizer.py    # 密码子优化
│   │   └── alphafold_client.py   # AlphaFold集成
│   ├── api/
│   │   └── routes.py             # API路由
│   ├── frontend/
│   │   └── ...                   # 前端界面
│   └── sequence_analysis.py      # 序列分析工具
├── docs/
│   └── ...                       # 文档
├── tests/
│   └── ...                       # 测试
├── examples/
│   └── ...                       # 示例
├── requirements.txt              # 依赖
└── README.md                     # 项目说明
```

---

## 📖 API文档

### SequenceAnalyzer

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `analyze` | sequence | Dict | 全面分析序列 |
| `calculate_gc_content` | sequence | float | 计算GC含量 |
| `translate` | sequence, table | str | 翻译为蛋白质 |
| `find_orfs` | sequence, min_length | List[Dict] | 查找ORF |
| `reverse_complement` | sequence | str | 反向互补 |

### CodonOptimizer

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `optimize` | protein_sequence | OptimizationResult | 优化密码子 |

### DNAEngine

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `design_dna` | protein_sequence, constraints | DesignResult | 设计DNA序列 |

---

## 🔬 应用案例

### 案例1：疫苗开发
- 优化病毒抗原基因序列
- 提高在大肠杆菌中的表达量
- 添加纯化标签

### 案例2：酶工程
- 设计具有特定活性的酶变体
- 优化热稳定性
- 改善底物特异性

### 案例3：生物燃料
- 设计代谢通路
- 优化关键酶的表达
- 提高产物产量

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📚 参考资料

- [Biopython](https://biopython.org/) - Python生物信息学工具包
- [AlphaFold](https://github.com/deepmind/alphafold) - 蛋白质结构预测
- [Codon Usage Database](https://www.kazusa.or.jp/codon/) - 密码子使用数据库
- [NCBI](https://www.ncbi.nlm.nih.gov/) - 国家生物技术信息中心
- [Addgene](https://www.addgene.org/) - 质粒库

---

## 📜 许可证

[MIT](LICENSE)

---

<div align="center">

**Made with ❤️ by AI 前沿社**

⭐ Star 支持我们！

</div>
