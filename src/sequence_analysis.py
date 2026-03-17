"""DNA 序列分析工具"""

from collections import Counter
from typing import Dict, List, Tuple


# 遗传密码表
CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}


class DNAAnalyzer:
    """DNA 序列分析器"""
    
    def __init__(self, sequence: str):
        self.sequence = sequence.upper()
        self._validate()
    
    def _validate(self):
        valid = set('ATCG')
        invalid = set(self.sequence) - valid
        if invalid:
            raise ValueError(f"Invalid bases: {invalid}")
    
    @property
    def length(self) -> int:
        return len(self.sequence)
    
    def gc_content(self) -> float:
        """GC 含量"""
        gc = sum(1 for b in self.sequence if b in 'GC')
        return gc / len(self.sequence) * 100
    
    def nucleotide_counts(self) -> Dict[str, int]:
        """碱基统计"""
        return dict(Counter(self.sequence))
    
    def reverse_complement(self) -> str:
        """反向互补链"""
        return ''.join(COMPLEMENT[b] for b in reversed(self.sequence))
    
    def transcribe(self) -> str:
        """转录为 mRNA"""
        return self.sequence.replace('T', 'U')
    
    def translate(self) -> str:
        """翻译为蛋白质序列"""
        mrna = self.transcribe()
        protein = []
        for i in range(0, len(mrna) - 2, 3):
            codon = mrna[i:i+3]
            if len(codon) == 3:
                aa = CODON_TABLE.get(codon, '?')
                if aa == '*':
                    break
                protein.append(aa)
        return ''.join(protein)
    
    def find_motif(self, motif: str) -> List[int]:
        """查找基序位置"""
        positions = []
        start = 0
        while True:
            pos = self.sequence.find(motif.upper(), start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        return positions
    
    def stats(self) -> str:
        """序列统计报告"""
        counts = self.nucleotide_counts()
        lines = [
            "=" * 40,
            "🧬 DNA Sequence Analysis Report",
            "=" * 40,
            f"  Length: {self.length} bp",
            f"  GC Content: {self.gc_content():.1f}%",
            f"  A: {counts.get('A', 0)} ({counts.get('A', 0)/self.length*100:.1f}%)",
            f"  T: {counts.get('T', 0)} ({counts.get('T', 0)/self.length*100:.1f}%)",
            f"  G: {counts.get('G', 0)} ({counts.get('G', 0)/self.length*100:.1f}%)",
            f"  C: {counts.get('C', 0)} ({counts.get('C', 0)/self.length*100:.1f}%)",
        ]
        
        mrna = self.transcribe()
        protein = self.translate()
        lines.extend([
            f"\n  mRNA (first 50): {mrna[:50]}...",
            f"  Protein (first 50): {protein[:50]}...",
        ])
        return '\n'.join(lines)


if __name__ == "__main__":
    # 示例：分析人类胰岛素基因片段
    sample = "ATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGACCCAGCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTCAGTCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAG"
    
    analyzer = DNAAnalyzer(sample)
    print(analyzer.stats())
    print("\n✅ Analysis complete!")
