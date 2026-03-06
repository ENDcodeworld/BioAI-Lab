"""
密码子优化算法模块
使用遗传算法和机器学习进行多目标密码子优化
"""
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class OptimizationConfig:
    """优化配置"""
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elitism_count: int = 5
    target_gc: Optional[float] = None
    target_cai: float = 0.9
    avoid_motifs: Optional[List[str]] = None
    weight_gc: float = 0.3
    weight_cai: float = 0.4
    weight_stability: float = 0.3


@dataclass
class OptimizationResult:
    """优化结果"""
    original_sequence: str
    optimized_sequence: str
    original_score: float
    optimized_score: float
    improvements: Dict[str, float]
    generations_run: int
    config: OptimizationConfig


class CodonOptimizer:
    """
    密码子优化器
    使用遗传算法进行多目标优化
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.codon_table = self._load_codon_table()
    
    def _load_codon_table(self) -> Dict[str, List[str]]:
        """加载标准密码子表"""
        return {
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
            '*': ['TAA', 'TAG', 'TGA'],
        }
    
    def _protein_to_codons(self, protein_sequence: str) -> List[List[str]]:
        """将蛋白质序列转换为可能的密码子列表"""
        protein_sequence = protein_sequence.upper().replace('*', '')
        codon_options = []
        
        for aa in protein_sequence:
            if aa in self.codon_table:
                codon_options.append(self.codon_table[aa])
            else:
                raise ValueError(f"Invalid amino acid: {aa}")
        
        return codon_options
    
    def _codons_to_sequence(self, codon_choice: List[str]) -> str:
        """将密码子选择转换为 DNA 序列"""
        return ''.join(codon_choice)
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """计算 GC 含量"""
        if not sequence:
            return 0.0
        gc_count = sequence.count('G') + sequence.count('C')
        return gc_count / len(sequence)
    
    def _calculate_cai(self, sequence: str) -> float:
        """
        计算密码子适应指数
        简化版本：基于最优密码子使用频率
        """
        # E. coli 最优密码子 (最高使用频率)
        optimal_codons = {
            'GCT', 'CGT', 'AAT', 'GAT', 'TGT', 'CAG', 'GAA', 'GGT',
            'CAT', 'ATT', 'CTG', 'AAA', 'ATG', 'TTT', 'CCT', 'TCT',
            'ACT', 'TGG', 'TAT', 'GTT'
        }
        
        sequence = sequence.upper()
        codons = [sequence[i:i+3] for i in range(0, len(sequence), 3)]
        
        optimal_count = sum(1 for codon in codons if codon in optimal_codons)
        return optimal_count / len(codons) if codons else 0.0
    
    def _calculate_stability(self, sequence: str) -> float:
        """
        计算序列稳定性评分
        基于：避免重复序列、均匀 GC 分布等
        """
        score = 100.0
        sequence = sequence.upper()
        
        # 惩罚长同聚物 (如 AAAAA)
        for base in 'ACGT':
            for length in range(5, 11):
                if base * length in sequence:
                    score -= 10 * (length - 4)
        
        # 惩罚 GC 极端区域 (滑动窗口)
        window_size = 20
        for i in range(0, len(sequence) - window_size, 5):
            window = sequence[i:i+window_size]
            gc = self._calculate_gc_content(window)
            if gc > 0.8 or gc < 0.2:
                score -= 5
        
        # 惩罚回文序列 (可能形成二级结构)
        for i in range(0, len(sequence) - 8, 2):
            subseq = sequence[i:i+8]
            if subseq == subseq[::-1]:
                score -= 2
        
        return max(0, score)
    
    def _fitness(self, sequence: str) -> float:
        """
        计算适应度函数
        多目标加权评分
        """
        scores = []
        weights = []
        
        # GC 含量评分
        gc = self._calculate_gc_content(sequence)
        if self.config.target_gc:
            gc_score = max(0, 100 - abs(gc - self.config.target_gc) * 200)
        else:
            # 默认目标 0.5
            gc_score = max(0, 100 - abs(gc - 0.5) * 150)
        scores.append(gc_score)
        weights.append(self.config.weight_gc)
        
        # CAI 评分
        cai = self._calculate_cai(sequence)
        cai_score = cai * 100
        scores.append(cai_score)
        weights.append(self.config.weight_cai)
        
        # 稳定性评分
        stability = self._calculate_stability(sequence)
        scores.append(stability)
        weights.append(self.config.weight_stability)
        
        # 惩罚 motif 违规
        if self.config.avoid_motifs:
            for motif in self.config.avoid_motifs:
                if motif.upper() in sequence:
                    scores[0] -= 20  # 从 GC 评分中扣除
        
        # 加权总分
        total = sum(s * w for s, w in zip(scores, weights))
        return total / sum(weights)
    
    def _create_individual(self, codon_options: List[List[str]]) -> List[str]:
        """创建初始个体 (随机密码子选择)"""
        return [random.choice(options) for options in codon_options]
    
    def _create_population(self, codon_options: List[List[str]], size: int) -> List[List[str]]:
        """创建初始种群"""
        return [self._create_individual(codon_options) for _ in range(size)]
    
    def _crossover(self, parent1: List[str], parent2: List[str]) -> Tuple[List[str], List[str]]:
        """单点交叉"""
        if len(parent1) != len(parent2):
            return parent1, parent2
        
        if random.random() > self.config.crossover_rate:
            return parent1, parent2
        
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        
        return child1, child2
    
    def _mutate(self, individual: List[str], codon_options: List[List[str]]) -> List[str]:
        """变异操作"""
        mutated = individual.copy()
        
        for i in range(len(mutated)):
            if random.random() < self.config.mutation_rate:
                # 随机选择一个不同的同义密码子
                alternatives = [c for c in codon_options[i] if c != mutated[i]]
                if alternatives:
                    mutated[i] = random.choice(alternatives)
        
        return mutated
    
    def _select_parents(self, population: List[List[str]], 
                       fitness_scores: List[float]) -> Tuple[List[str], List[str]]:
        """锦标赛选择"""
        def tournament():
            idx1, idx2 = random.sample(range(len(population)), 2)
            if fitness_scores[idx1] > fitness_scores[idx2]:
                return population[idx1]
            return population[idx2]
        
        return tournament(), tournament()
    
    def optimize(self, protein_sequence: str) -> OptimizationResult:
        """
        执行密码子优化
        
        Args:
            protein_sequence: 蛋白质序列
        
        Returns:
            OptimizationResult: 优化结果
        """
        codon_options = self._protein_to_codons(protein_sequence)
        
        # 创建初始种群
        population = self._create_population(codon_options, self.config.population_size)
        
        best_individual = None
        best_fitness = -float('inf')
        
        for generation in range(self.config.generations):
            # 计算适应度
            fitness_scores = []
            for individual in population:
                sequence = self._codons_to_sequence(individual)
                fitness = self._fitness(sequence)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
            
            # 精英保留
            elite_indices = sorted(
                range(len(fitness_scores)), 
                key=lambda i: fitness_scores[i], 
                reverse=True
            )[:self.config.elitism_count]
            
            elites = [population[i] for i in elite_indices]
            
            # 创建新一代
            new_population = elites.copy()
            
            while len(new_population) < self.config.population_size:
                # 选择父母
                parent1, parent2 = self._select_parents(population, fitness_scores)
                
                # 交叉
                child1, child2 = self._crossover(parent1, parent2)
                
                # 变异
                child1 = self._mutate(child1, codon_options)
                child2 = self._mutate(child2, codon_options)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.config.population_size]
        
        # 生成结果
        optimized_sequence = self._codons_to_sequence(best_individual)
        original_sequence = self._codons_to_sequence(
            self._create_individual(codon_options)
        )
        
        return OptimizationResult(
            original_sequence=original_sequence,
            optimized_sequence=optimized_sequence,
            original_score=self._fitness(original_sequence),
            optimized_score=best_fitness,
            improvements={
                'fitness': best_fitness - self._fitness(original_sequence),
                'gc_content': self._calculate_gc_content(optimized_sequence) - 
                             self._calculate_gc_content(original_sequence),
                'cai': self._calculate_cai(optimized_sequence) - 
                      self._calculate_cai(original_sequence),
            },
            generations_run=self.config.generations,
            config=self.config,
        )
    
    def optimize_batch(self, 
                      protein_sequences: List[str],
                      max_workers: int = 4) -> List[OptimizationResult]:
        """批量优化多个蛋白质序列"""
        results = []
        
        # 简单串行实现 (可改为多进程)
        for seq in protein_sequences:
            try:
                result = self.optimize(seq)
                results.append(result)
            except Exception as e:
                results.append(OptimizationResult(
                    original_sequence=seq,
                    optimized_sequence="",
                    original_score=0,
                    optimized_score=0,
                    improvements={},
                    generations_run=0,
                    config=self.config,
                ))
        
        return results


# 便捷函数
def optimize_codons(protein_sequence: str, **kwargs) -> OptimizationResult:
    """便捷函数：优化密码子"""
    config = OptimizationConfig(**kwargs) if kwargs else OptimizationConfig()
    optimizer = CodonOptimizer(config)
    return optimizer.optimize(protein_sequence)


def compare_sequences(seq1: str, seq2: str) -> Dict:
    """比较两个 DNA 序列"""
    def calc_metrics(seq):
        optimizer = CodonOptimizer()
        return {
            'gc_content': optimizer._calculate_gc_content(seq),
            'cai': optimizer._calculate_cai(seq),
            'stability': optimizer._calculate_stability(seq),
            'fitness': optimizer._fitness(seq),
        }
    
    return {
        'sequence1': calc_metrics(seq1),
        'sequence2': calc_metrics(seq2),
        'differences': {
            'gc_diff': calc_metrics(seq2)['gc_content'] - calc_metrics(seq1)['gc_content'],
            'cai_diff': calc_metrics(seq2)['cai'] - calc_metrics(seq1)['cai'],
            'stability_diff': calc_metrics(seq2)['stability'] - calc_metrics(seq1)['stability'],
        }
    }
