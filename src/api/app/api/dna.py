"""
DNA Design Router
DNA 序列设计 API 接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import sys
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.dna_engine import DNADesignEngine, HostOrganism, DesignResult, analyze_dna
from ai.codon_optimizer import CodonOptimizer, OptimizationConfig, optimize_codons

router = APIRouter()


class DNADesignRequest(BaseModel):
    protein_sequence: str
    host_organism: str = "e_coli"
    optimization_targets: Optional[Dict[str, float]] = None
    avoid_enzymes: Optional[List[str]] = None


class DNADesignResponse(BaseModel):
    sequence: str
    protein_sequence: str
    length: int
    gc_content: float
    cai: float
    score: float
    violations: List[str]
    metadata: Dict


class OptimizeRequest(BaseModel):
    protein_sequence: str
    target_gc: Optional[float] = None
    target_cai: float = 0.9
    avoid_motifs: Optional[List[str]] = None


class AnalyzeResponse(BaseModel):
    length: int
    gc_content: float
    cai: float
    codon_usage: Dict[str, int]
    restriction_sites: Dict[str, List[int]]
    num_codons: int


@router.post("/design", response_model=DNADesignResponse)
async def design_dna(request: DNADesignRequest):
    """
    从蛋白质序列设计 DNA 序列
    
    功能:
    - 密码子优化 (针对特定宿主)
    - GC 含量控制
    - 避免特定酶切位点
    """
    try:
        # 映射宿主生物
        try:
            host = HostOrganism(request.host_organism)
        except ValueError:
            host = HostOrganism.E_COLI
        
        # 创建引擎
        engine = DNADesignEngine(host)
        
        # 执行设计
        result = engine.design(
            protein_sequence=request.protein_sequence,
            optimization_targets=request.optimization_targets,
            avoid_enzymes=request.avoid_enzymes
        )
        
        return DNADesignResponse(
            sequence=result.sequence,
            protein_sequence=result.protein_sequence,
            length=result.length,
            gc_content=round(result.gc_content, 4),
            cai=round(result.cai, 4),
            score=result.score,
            violations=result.violations,
            metadata=result.metadata,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design failed: {str(e)}")


@router.post("/optimize", response_model=DNADesignResponse)
async def optimize_sequence(request: OptimizeRequest):
    """
    使用遗传算法优化密码子
    
    多目标优化:
    - GC 含量
    - 密码子适应指数 (CAI)
    - 序列稳定性
    """
    try:
        config = OptimizationConfig(
            target_gc=request.target_gc,
            target_cai=request.target_cai,
            avoid_motifs=request.avoid_motifs,
            population_size=100,
            generations=50,
        )
        
        optimizer = CodonOptimizer(config)
        result = optimizer.optimize(request.protein_sequence)
        
        # 分析优化后的序列
        engine = DNADesignEngine()
        analysis = engine.analyze(result.optimized_sequence)
        
        return DNADesignResponse(
            sequence=result.optimized_sequence,
            protein_sequence=request.protein_sequence.upper().replace('*', ''),
            length=len(result.optimized_sequence),
            gc_content=round(analysis['gc_content'], 4),
            cai=round(analysis['cai'], 4),
            score=analysis['cai'] * 100,
            violations=[],
            metadata={
                'original_score': result.original_score,
                'optimized_score': result.optimized_score,
                'improvements': result.improvements,
                'generations': result.generations_run,
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_sequence(sequence: str):
    """
    分析 DNA 序列
    
    返回:
    - GC 含量
    - 密码子适应指数
    - 密码子使用统计
    - 限制性内切酶位点
    """
    try:
        result = analyze_dna(sequence)
        return AnalyzeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/codon-table")
async def get_codon_table(host: str = "e_coli"):
    """获取密码子表"""
    try:
        host_enum = HostOrganism(host) if host in [h.value for h in HostOrganism] else HostOrganism.E_COLI
        engine = DNADesignEngine(host_enum)
        
        return {
            'host': host,
            'codon_table': engine.codon_table,
            'codon_usage': engine.codon_usage,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
