"""
DNA序列分析工具
提供序列统计、特征提取和序列比对功能
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter
import numpy as np


class SequenceAnalyzer:
    """DNA序列分析器"""
    
    def __init__(self):
        self.nucleotides = ['A', 'T', 'C', 'G']
        self.complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    
    def analyze(self, sequence: str) -> Dict:
        """
        全面分析DNA序列
        
        Args:
            sequence: DNA序列
            
        Returns:
            分析结果字典
        """
        sequence = sequence.upper().replace(' ', '').replace('\n', '')
        
        return {
            'length': len(sequence),
            'gc_content': self.calculate_gc_content(sequence),
            'nucleotide_counts': self.count_nucleotides(sequence),
            'gc_skew': self.calculate_gc_skew(sequence),
            'at_skew': self.calculate_at_skew(sequence),
            ' molecular_weight': self.calculate_molecular_weight(sequence),
            'melting_temp': self.estimate_tm(sequence),
            'orf_info': self.find_orfs(sequence),
            'repeats': self.find_repeats(sequence),
            'complexity': self.calculate_complexity(sequence)
        }
    
    def calculate_gc_content(self, sequence: str) -> float:
        """计算GC含量"""
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence) if sequence else 0.0
    
    def count_nucleotides(self, sequence: str) -> Dict[str, int]:
        """统计核苷酸数量"""
        sequence = sequence.upper()
        return {
            'A': sequence.count('A'),
            'T': sequence.count('T'),
            'C': sequence.count('C'),
            'G': sequence.count('G'),
            'N': sequence.count('N')  # 未知碱基
        }
    
    def calculate_gc_skew(self, sequence: str, window: int = 1000) -> List[float]:
        """
        计算GC偏度 (G-C)/(G+C)
        用于识别复制起点等特征
        """
        sequence = sequence.upper()
        skews = []
        
        for i in range(0, len(sequence) - window + 1, window // 2):
            window_seq = sequence[i:i+window]
            g = window_seq.count('G')
            c = window_seq.count('C')
            
            if g + c > 0:
                skew = (g - c) / (g + c)
            else:
                skew = 0
            
            skews.append(skew)
        
        return skews
    
    def calculate_at_skew(self, sequence: str) -> float:
        """计算AT偏度 (A-T)/(A+T)"""
        sequence = sequence.upper()
        a = sequence.count('A')
        t = sequence.count('T')
        
        if a + t > 0:
            return (a - t) / (a + t)
        return 0.0
    
    def calculate_molecular_weight(self, sequence: str) -> float:
        """计算分子量 (g/mol)"""
        sequence = sequence.upper()
        
        # 平均分子量 (道尔顿)
        weights = {'A': 313.21, 'T': 304.2, 'C': 289.18, 'G': 329.21}
        
        mw = sum(weights.get(base, 0) for base in sequence)
        
        # 减去水分子 (形成磷酸二酯键)
        mw -= 61.96 * (len(sequence) - 1)
        
        return mw
    
    def estimate_tm(self, sequence: str, salt_conc: float = 50.0) -> float:
        """
        估算熔解温度 (Wallace方法)
        
        Args:
            sequence: DNA序列
            salt_conc: 盐浓度 (mM)
        """
        sequence = sequence.upper()
        
        if len(sequence) < 14:
            # 短序列: Wallace法则
            tm = 2 * (sequence.count('A') + sequence.count('T')) + \
                 4 * (sequence.count('G') + sequence.count('C'))
        else:
            # 长序列: 改进的Wallace法则
            gc_content = self.calculate_gc_content(sequence)
            tm = 81.5 + 0.41 * gc_content * 100 - 675 / len(sequence)
            tm += 16.6 * np.log10(salt_conc / 1000)
        
        return tm
    
    def reverse_complement(self, sequence: str) -> str:
        """计算反向互补序列"""
        return ''.join(self.complement.get(base, base) for base in reversed(sequence.upper()))
    
    def find_orfs(self, sequence: str, min_length: int = 100) -> List[Dict]:
        """
        寻找开放阅读框 (ORF)
        
        Args:
            sequence: DNA序列
            min_length: 最小ORF长度（氨基酸）
            
        Returns:
            ORF列表
        """
        sequence = sequence.upper()
        start_codon = 'ATG'
        stop_codons = ['TAA', 'TAG', 'TGA']
        
        orfs = []
        
        for frame in range(3):
            i = frame
            while i < len(sequence) - 2:
                codon = sequence[i:i+3]
                
                if codon == start_codon:
                    # 找到起始密码子
                    for j in range(i + 3, len(sequence) - 2, 3):
                        stop_codon = sequence[j:j+3]
                        
                        if stop_codon in stop_codons:
                            # 找到终止密码子
                            orf_length = (j - i) // 3
                            
                            if orf_length >= min_length:
                                orfs.append({
                                    'start': i,
                                    'end': j + 3,
                                    'length_nt': j - i + 3,
                                    'length_aa': orf_length,
                                    'frame': frame + 1,
                                    'sequence': sequence[i:j+3]
                                })
                            
                            i = j + 3
                            break
                    else:
                        i += 3
                else:
                    i += 3
        
        return sorted(orfs, key=lambda x: x['length_aa'], reverse=True)
    
    def translate(self, sequence: str, table: int = 1) -> str:
        """
        翻译DNA为蛋白质
        
        Args:
            sequence: DNA序列
            table: 遗传密码表编号 (1=标准)
        """
        sequence = sequence.upper()
        
        # 标准遗传密码
        codon_table = {
            'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
            'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
            'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
            'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
            'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
            'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
            'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
            'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
            'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
            'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
            'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
            'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
            'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
            'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
            'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
            'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
        }
        
        protein = ''
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            protein += codon_table.get(codon, '?')
        
        return protein
    
    def find_repeats(self, sequence: str, min_repeat_length: int = 3, min_repeats: int = 3) -> List[Dict]:
        """寻找重复序列"""
        sequence = sequence.upper()
        repeats = []
        
        for length in range(min_repeat_length, min_repeat_length + 10):
            for i in range(len(sequence) - length * min_repeats + 1):
                pattern = sequence[i:i+length]
                count = 1
                j = i + length
                
                while j + length <= len(sequence) and sequence[j:j+length] == pattern:
                    count += 1
                    j += length
                
                if count >= min_repeats:
                    repeats.append({
                        'pattern': pattern,
                        'start': i,
                        'length': length,
                        'count': count,
                        'total_length': length * count
                    })
        
        # 去重（保留最长的）
        repeats = sorted(repeats, key=lambda x: x['total_length'], reverse=True)
        filtered = []
        seen = set()
        
        for r in repeats:
            if r['start'] not in seen:
                filtered.append(r)
                for i in range(r['start'], r['start'] + r['total_length']):
                    seen.add(i)
        
        return filtered[:10]
    
    def calculate_complexity(self, sequence: str, window: int = 100) -> float:
        """
        计算序列复杂度（基于Shannon熵）
        """
        sequence = sequence.upper()
        
        if len(sequence) < window:
            window = len(sequence)
        
        complexities = []
        
        for i in range(0, len(sequence) - window + 1, window // 2):
            window_seq = sequence[i:i+window]
            counts = Counter(window_seq)
            
            # Shannon熵
            entropy = 0
            for count in counts.values():
                p = count / window
                if p > 0:
                    entropy -= p * np.log2(p)
            
            # 归一化到0-1
            max_entropy = np.log2(4)  # 4种核苷酸
            complexity = entropy / max_entropy
            
            complexities.append(complexity)
        
        return np.mean(complexities) if complexities else 0.0


class SequenceAligner:
    """简单序列比对"""
    
    def simple_align(self, seq1: str, seq2: str) -> Tuple[str, str, float]:
        """
        简单全局比对（Needleman-Wunsch简化版）
        
        Returns:
            (对齐序列1, 对齐序列2, 相似度)
        """
        seq1 = seq1.upper()
        seq2 = seq2.upper()
        
        # 简单计算：直接比较
        min_len = min(len(seq1), len(seq2))
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        
        similarity = matches / max(len(seq1), len(seq2))
        
        return seq1, seq2, similarity


def demo():
    """演示"""
    print("=" * 60)
    print("🧬 BioAI-Lab - DNA序列分析工具")
    print("=" * 60)
    
    # 示例序列（GFP基因片段）
    sequence = """
    ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGG
    GCACAAATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTT
    GCACTACTGGAAAACTACCTGTTCCATGGCCAACACTTGTCACTACTTTCTCTTATGGTGTTCAATGCTTT
    TCAAGATACCCAGATCATATGAAACGGCATGACTTTTTCAAGAGTGCCATGCCCGAAGGTTATGTACAGG
    AAAGAACTATATTTTTCAAAGATGACGGGAACTACAAGACACGTGCTGAAGTCAAGTTTGAAGGTGATAC
    CCTTGCCAATCGGATTTGAGTTTAAACGAGATACATATGAACGGCATACACTTCTTCAAGACAGAACATC
    AAAAGATGACGATACAACATGAATTAAAAGTGACGGAAAACTTAAATGAAAGATACAAAGGTAAAGAAAG
    AATTTTCACTGGAAGTTGACACTTCTCAACAAAAATACATCATTGATGGTGAAGTTAAAACCACAAAGAT
    """.replace('\n', '').replace(' ', '')
    
    print(f"\n📋 分析序列 (GFP基因片段):")
    print(f"   序列长度: {len(sequence)} bp")
    
    analyzer = SequenceAnalyzer()
    results = analyzer.analyze(sequence)
    
    print("\n📊 分析结果:")
    print("-" * 40)
    print(f"   GC含量: {results['gc_content']*100:.2f}%")
    print(f"   分子量: {results['molecular_weight']/1000:.2f} kDa")
    print(f"   熔解温度: {results['melting_temp']:.1f}°C")
    print(f"   复杂度: {results['complexity']*100:.1f}%")
    
    print(f"\n   核苷酸统计:")
    for base, count in results['nucleotide_counts'].items():
        pct = count / results['length'] * 100
        print(f"      {base}: {count} ({pct:.1f}%)")
    
    print(f"\n   开放阅读框 (ORF):")
    for i, orf in enumerate(results['orf_info'][:3], 1):
        print(f"      ORF {i}: 位置 {orf['start']}-{orf['end']}, "
              f"长度 {orf['length_aa']} 氨基酸")
    
    # 翻译
    print(f"\n   蛋白质序列 (前50个氨基酸):")
    protein = analyzer.translate(sequence[:150])
    print(f"      {protein[:50]}")
    
    # 反向互补
    print(f"\n   反向互补序列 (前30bp):")
    rev_comp = analyzer.reverse_complement(sequence[:30])
    print(f"      原始: {sequence[:30]}")
    print(f"      互补: {rev_comp}")
    
    print("\n" + "=" * 60)
    print("✅ DNA序列分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo()
