"""
DNA Sequence Design Engine
核心 DNA 序列设计引擎，支持密码子优化、GC 含量控制、酶切位点管理
"""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HostOrganism(Enum):
    """宿主生物类型"""
    E_COLI = "e_coli"
    S_CEREVISIAE = "s_cerevisiae"
    HUMAN = "human"
    A_THALIANA = "a_thaliana"
    CUSTOM = "custom"


@dataclass
class DesignResult:
    """DNA 设计结果"""
    sequence: str
    protein_sequence: str
    length: int
    gc_content: float
    cai: float  # Codon Adaptation Index
    score: float
    violations: List[str]
    metadata: Dict


# 标准遗传密码表
STANDARD_CODON_TABLE = {
    'A': ['GCT', 'GCC', 'GCA', 'GCG'],
    'R': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
    'N': ['AAT', 'AAC'],
    'D': ['GAT', 'GAC'],
    'C': ['TGT', 'TGC'],
    'Q': ['CAA', 'CAG'],
    'E': ['GAA', 'GAG'],
    'G': ['GGT', 'GGC', 'GGA', 'GGG'],
    'H': ['CAT', 'CAC'],
    'I': ['ATT', 'ATC', 'ATA'],
    'L': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
    'K': ['AAA', 'AAG'],
    'M': ['ATG'],
    'F': ['TTT', 'TTC'],
    'P': ['CCT', 'CCC', 'CCA', 'CCG'],
    'S': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'],
    'T': ['ACT', 'ACC', 'ACA', 'ACG'],
    'W': ['TGG'],
    'Y': ['TAT', 'TAC'],
    'V': ['GTT', 'GTC', 'GTA', 'GTG'],
    '*': ['TAA', 'TAG', 'TGA'],  # 终止密码子
}

# 不同宿主的密码子使用频率 (简化版)
CODON_USAGE = {
    HostOrganism.E_COLI: {
        'A': [0.40, 0.32, 0.18, 0.10],
        'R': [0.35, 0.36, 0.07, 0.07, 0.07, 0.08],
        'N': [0.55, 0.45],
        'D': [0.52, 0.48],
        'C': [0.57, 0.43],
        'Q': [0.35, 0.65],
        'E': [0.34, 0.66],
        'G': [0.36, 0.35, 0.15, 0.14],
        'H': [0.57, 0.43],
        'I': [0.49, 0.39, 0.12],
        'L': [0.13, 0.13, 0.11, 0.11, 0.06, 0.46],
        'K': [0.74, 0.26],
        'M': [1.0],
        'F': [0.59, 0.41],
        'P': [0.33, 0.36, 0.18, 0.13],
        'S': [0.31, 0.33, 0.13, 0.10, 0.07, 0.06],
        'T': [0.38, 0.36, 0.14, 0.12],
        'W': [1.0],
        'Y': [0.59, 0.41],
        'V': [0.40, 0.36, 0.11, 0.13],
        '*': [0.57, 0.35, 0.08],
    },
    HostOrganism.HUMAN: {
        'A': [0.27, 0.41, 0.17, 0.15],
        'R': [0.19, 0.34, 0.11, 0.11, 0.11, 0.14],
        'N': [0.47, 0.53],
        'D': [0.47, 0.53],
        'C': [0.44, 0.56],
        'Q': [0.27, 0.73],
        'E': [0.28, 0.72],
        'G': [0.25, 0.40, 0.16, 0.19],
        'H': [0.43, 0.57],
        'I': [0.36, 0.47, 0.17],
        'L': [0.13, 0.13, 0.13, 0.19, 0.07, 0.35],
        'K': [0.43, 0.57],
        'M': [1.0],
        'F': [0.46, 0.54],
        'P': [0.28, 0.32, 0.20, 0.20],
        'S': [0.23, 0.29, 0.13, 0.13, 0.11, 0.11],
        'T': [0.24, 0.36, 0.18, 0.22],
        'W': [1.0],
        'Y': [0.44, 0.56],
        'V': [0.18, 0.27, 0.21, 0.34],
        '*': [0.26, 0.20, 0.54],
    },
}


class DNADesignEngine:
    """DNA 序列设计引擎"""
    
    def __init__(self, host_organism: HostOrganism = HostOrganism.E_COLI):
        self.host = host_organism
        self.codon_table = STANDARD_CODON_TABLE
        self.codon_usage = CODON_USAGE.get(host_organism, CODON_USAGE[HostOrganism.E_COLI])
        self.restriction_sites = self._load_common_restriction_sites()
    
    def _load_common_restriction_sites(self) -> Dict[str, str]:
        """加载常见限制性内切酶位点"""
        return {
            'EcoRI': 'GAATTC',
            'BamHI': 'GGATCC',
            'HindIII': 'AAGCTT',
            'NotI': 'GCGGCCGC',
            'XhoI': 'CTCGAG',
            'NdeI': 'CATATG',
            'NcoI': 'CCATGG',
            'SacI': 'GAGCTC',
            'KpnI': 'GGTACC',
            'PstI': 'CTGCAG',
        }
    
    def protein_to_dna(self, protein_sequence: str) -> str:
        """将蛋白质序列转换为初始 DNA 序列 (随机密码子选择)"""
        dna_seq = []
        protein_sequence = protein_sequence.upper().replace('*', '')
        
        for aa in protein_sequence:
            if aa not in self.codon_table:
                raise ValueError(f"Invalid amino acid: {aa}")
            codons = self.codon_table[aa]
            dna_seq.append(random.choice(codons))
        
        return ''.join(dna_seq)
    
    def calculate_gc_content(self, sequence: str) -> float:
        """计算 GC 含量"""
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0.0
    
    def calculate_cai(self, sequence: str) -> float:
        """
        计算密码子适应指数 (Codon Adaptation Index)
        CAI 越接近 1，表示密码子使用越优化
        """
        sequence = sequence.upper()
        if len(sequence) % 3 != 0:
            raise ValueError("Sequence length must be multiple of 3")
        
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]
        
        # 反向密码子表：codon -> amino acid
        codon_to_aa = {}
        for aa, codon_list in self.codon_table.items():
            for codon in codon_list:
                codon_to_aa[codon] = aa
        
        cai_values = []
        for codon in codons:
            if codon not in codon_to_aa:
                continue
            aa = codon_to_aa[codon]
            usage = self.codon_usage.get(aa, {})
            
            # 获取该密码子的使用频率
            codon_idx = self.codon_table[aa].index(codon) if codon in self.codon_table[aa] else 0
            freq = usage.get(aa, [1.0/len(self.codon_table[aa])])[codon_idx] if isinstance(usage.get(aa), list) else 1.0
            
            if freq > 0:
                cai_values.append(freq)
        
        if not cai_values:
            return 0.0
        
        # 几何平均数
        from math import exp, log
        return exp(sum(log(v) for v in cai_values) / len(cai_values))
    
    def find_restriction_sites(self, sequence: str) -> Dict[str, List[int]]:
        """查找序列中的限制性内切酶位点"""
        sequence = sequence.upper()
        sites = {}
        
        for enzyme, site_seq in self.restriction_sites.items():
            positions = []
            start = 0
            while True:
                pos = sequence.find(site_seq, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if positions:
                sites[enzyme] = positions
        
        return sites
    
    def optimize_codons(self, 
                       protein_sequence: str,
                       target_gc: Optional[float] = None,
                       avoid_sites: Optional[List[str]] = None) -> str:
        """
        密码子优化
        
        Args:
            protein_sequence: 蛋白质序列
            target_gc: 目标 GC 含量 (0-1)
            avoid_sites: 需要避免的酶切位点列表
        
        Returns:
            优化后的 DNA 序列
        """
        protein_sequence = protein_sequence.upper().replace('*', '')
        
        # 1. 根据宿主偏好选择初始密码子
        dna_seq = []
        for aa in protein_sequence:
            if aa not in self.codon_table:
                continue
            
            codons = self.codon_table[aa]
            usage = self.codon_usage.get(aa, [1.0/len(codons)] * len(codons))
            
            if isinstance(usage, list) and len(usage) == len(codons):
                # 按使用频率加权选择
                codon = random.choices(codons, weights=usage, k=1)[0]
            else:
                codon = random.choice(codons)
            
            dna_seq.append(codon)
        
        sequence = ''.join(dna_seq)
        
        # 2. GC 含量优化 (如果需要)
        if target_gc is not None:
            sequence = self._optimize_gc_content(sequence, target_gc)
        
        # 3. 避免特定酶切位点
        if avoid_sites:
            sequence = self._avoid_restriction_sites(sequence, protein_sequence, avoid_sites)
        
        return sequence
    
    def _optimize_gc_content(self, sequence: str, target_gc: float, max_iterations: int = 100) -> str:
        """优化 GC 含量到目标值"""
        sequence = sequence.upper()
        current_gc = self.calculate_gc_content(sequence)
        
        if abs(current_gc - target_gc) < 0.01:
            return sequence
        
        # 将序列转换为密码子列表
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]
        
        # 反向密码子表
        codon_to_aa = {}
        for aa, codon_list in self.codon_table.items():
            for codon in codon_list:
                codon_to_aa[codon] = aa
        
        for iteration in range(max_iterations):
            current_gc = self.calculate_gc_content(sequence)
            if abs(current_gc - target_gc) < 0.01:
                break
            
            # 随机选择一个密码子进行替换
            idx = random.randint(0, len(codons) - 1)
            aa = codon_to_aa.get(codons[idx])
            
            if not aa or len(self.codon_table[aa]) <= 1:
                continue
            
            # 选择 GC 含量不同的同义密码子
            current_codon = codons[idx]
            current_gc_codon = (current_codon.count('G') + current_codon.count('C')) / 3
            
            alternative_codons = [c for c in self.codon_table[aa] if c != current_codon]
            
            if not alternative_codons:
                continue
            
            # 根据目标 GC 选择合适的密码子
            if target_gc > current_gc:
                # 需要增加 GC，选择 GC 含量更高的密码子
                best_codon = max(alternative_codons, 
                               key=lambda c: (c.count('G') + c.count('C')) / 3)
            else:
                # 需要降低 GC，选择 GC 含量更低的密码子
                best_codon = min(alternative_codons, 
                               key=lambda c: (c.count('G') + c.count('C')) / 3)
            
            codons[idx] = best_codon
            sequence = ''.join(codons)
        
        return sequence
    
    def _avoid_restriction_sites(self, 
                                 sequence: str, 
                                 protein_sequence: str,
                                 sites_to_avoid: List[str]) -> str:
        """通过同义密码子替换避免特定酶切位点"""
        sequence = sequence.upper()
        
        # 反向密码子表
        codon_to_aa = {}
        for aa, codon_list in self.codon_table.items():
            for codon in codon_list:
                codon_to_aa[codon] = aa
        
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]
        
        for enzyme_name in sites_to_avoid:
            if enzyme_name not in self.restriction_sites:
                continue
            
            site_seq = self.restriction_sites[enzyme_name]
            
            # 查找所有该酶切位点
            start = 0
            while True:
                pos = sequence.find(site_seq, start)
                if pos == -1:
                    break
                
                # 尝试通过同义密码子替换破坏该位点
                # 简单策略：改变位点中间的一个密码子
                affected_codon_idx = (pos + len(site_seq) // 2) // 3
                
                if affected_codon_idx < len(codons):
                    aa = codon_to_aa.get(codons[affected_codon_idx])
                    if aa and len(self.codon_table[aa]) > 1:
                        # 选择一个不同的同义密码子
                        alternatives = [c for c in self.codon_table[aa] if c != codons[affected_codon_idx]]
                        if alternatives:
                            codons[affected_codon_idx] = random.choice(alternatives)
                            sequence = ''.join(codons)
                
                start = pos + 1
        
        return sequence
    
    def design(self,
              protein_sequence: str,
              optimization_targets: Optional[Dict[str, float]] = None,
              avoid_enzymes: Optional[List[str]] = None) -> DesignResult:
        """
        完整 DNA 设计流程
        
        Args:
            protein_sequence: 目标蛋白质序列
            optimization_targets: 优化目标 {gc_content: 0.5, cai: 0.9}
            avoid_enzymes: 需要避免的酶切位点
        
        Returns:
            DesignResult: 设计结果
        """
        optimization_targets = optimization_targets or {}
        avoid_enzymes = avoid_enzymes or []
        
        # 1. 密码子优化
        target_gc = optimization_targets.get('gc_content')
        sequence = self.optimize_codons(
            protein_sequence,
            target_gc=target_gc,
            avoid_sites=avoid_enzymes
        )
        
        # 2. 计算指标
        gc_content = self.calculate_gc_content(sequence)
        cai = self.calculate_cai(sequence)
        
        # 3. 检查违规
        violations = []
        restriction_sites = self.find_restriction_sites(sequence)
        
        for enzyme in avoid_enzymes:
            if enzyme in restriction_sites:
                violations.append(f"Found {enzyme} site at positions {restriction_sites[enzyme]}")
        
        if target_gc and abs(gc_content - target_gc) > 0.05:
            violations.append(f"GC content {gc_content:.2f} deviates from target {target_gc}")
        
        # 4. 计算综合评分
        score = self._calculate_score(sequence, optimization_targets)
        
        return DesignResult(
            sequence=sequence,
            protein_sequence=protein_sequence.upper().replace('*', ''),
            length=len(sequence),
            gc_content=gc_content,
            cai=cai,
            score=score,
            violations=violations,
            metadata={
                'host_organism': self.host.value,
                'restriction_sites_found': {k: len(v) for k, v in restriction_sites.items()},
                'optimization_targets': optimization_targets,
            }
        )
    
    def _calculate_score(self, sequence: str, targets: Dict[str, float]) -> float:
        """计算综合评分 (0-100)"""
        scores = []
        weights = []
        
        # GC 含量评分
        if 'gc_content' in targets:
            actual_gc = self.calculate_gc_content(sequence)
            gc_score = max(0, 100 - abs(actual_gc - targets['gc_content']) * 200)
            scores.append(gc_score)
            weights.append(0.3)
        
        # CAI 评分
        cai = self.calculate_cai(sequence)
        cai_score = cai * 100
        scores.append(cai_score)
        weights.append(0.4)
        
        # 酶切位点评分 (无违规得满分)
        restriction_sites = self.find_restriction_sites(sequence)
        enzyme_score = max(0, 100 - len(restriction_sites) * 5)
        scores.append(enzyme_score)
        weights.append(0.3)
        
        # 加权平均
        total_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        return round(total_score, 2)
    
    def analyze(self, sequence: str) -> Dict:
        """
        分析 DNA 序列
        
        Returns:
            包含 GC 含量、密码子使用、酶切位点等信息
        """
        sequence = sequence.upper()
        
        # 密码子统计
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3) if len(sequence[i:i+3]) == 3]
        codon_counts = {}
        for codon in codons:
            codon_counts[codon] = codon_counts.get(codon, 0) + 1
        
        return {
            'length': len(sequence),
            'gc_content': self.calculate_gc_content(sequence),
            'cai': self.calculate_cai(sequence),
            'codon_usage': codon_counts,
            'restriction_sites': self.find_restriction_sites(sequence),
            'num_codons': len(codons),
        }


# 便捷函数
def design_dna(protein_sequence: str, 
               host: str = "e_coli",
               **kwargs) -> DesignResult:
    """便捷函数：设计 DNA 序列"""
    host_enum = HostOrganism(host) if host in [h.value for h in HostOrganism] else HostOrganism.E_COLI
    engine = DNADesignEngine(host_enum)
    return engine.design(protein_sequence, **kwargs)


def analyze_dna(sequence: str) -> Dict:
    """便捷函数：分析 DNA 序列"""
    engine = DNADesignEngine()
    return engine.analyze(sequence)
