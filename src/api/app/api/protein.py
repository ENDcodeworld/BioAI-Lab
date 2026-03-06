"""
Protein Prediction Router
蛋白质结构预测 API 接口
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.alphafold_client import (
    AlphaFoldClient, 
    PredictionModel, 
    PredictionRequest,
    JobStatus,
    predict_structure,
    analyze_structure,
)
from visualization.protein_viewer import ProteinVisualizer, visualize_pdb

router = APIRouter()

# 全局客户端 (本地模式用于演示)
_client: Optional[AlphaFoldClient] = None


def get_client() -> AlphaFoldClient:
    """获取或创建 AlphaFold 客户端"""
    global _client
    if _client is None:
        _client = AlphaFoldClient(local_mode=True)
    return _client


class ProteinPredictRequest(BaseModel):
    sequence: str
    model: str = "esmfold"
    num_recycles: int = 3
    return_confidence: bool = True


class ProteinPredictResponse(BaseModel):
    job_id: str
    status: str
    sequence: str
    model: str
    plddt_score: Optional[float] = None
    processing_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ProteinAnalyzeResponse(BaseModel):
    total_residues: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    average_plddt: Optional[float]
    quality: str


@router.post("/predict", response_model=ProteinPredictResponse)
async def predict_protein(request: ProteinPredictRequest):
    """
    预测蛋白质 3D 结构
    
    支持的模型:
    - esmfold: 快速预测 (推荐)
    - alphafold2: 高精度预测
    - openfold: 开源实现
    """
    try:
        client = get_client()
        
        # 映射模型
        try:
            model = PredictionModel(request.model)
        except ValueError:
            model = PredictionModel.ESMFOLD
        
        # 提交预测
        pred_request = PredictionRequest(
            sequence=request.sequence,
            model=model,
            num_recycles=request.num_recycles,
            return_confidence=request.return_confidence,
        )
        
        result = await client.submit_prediction(pred_request)
        
        # 构建响应
        response_data = {
            'job_id': result.job_id,
            'status': result.status.value,
            'sequence': result.sequence,
            'model': result.model,
            'plddt_score': result.plddt_score,
            'processing_time': result.processing_time,
        }
        
        if result.status == JobStatus.COMPLETED:
            response_data['result'] = {
                'pdb_available': result.pdb_file is not None,
                'confidence_scores_available': result.confidence_scores is not None,
                'num_residues': len(result.sequence),
            }
        elif result.status == JobStatus.FAILED:
            response_data['error_message'] = result.error_message
        
        return ProteinPredictResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/predict/{job_id}", response_model=ProteinPredictResponse)
async def get_prediction(job_id: str):
    """
    获取预测任务状态和结果
    """
    try:
        client = get_client()
        result = await client.get_prediction(job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return ProteinPredictResponse(
            job_id=result.job_id,
            status=result.status.value,
            sequence=result.sequence,
            model=result.model,
            plddt_score=result.plddt_score,
            processing_time=result.processing_time,
            result={'pdb_available': result.pdb_file is not None} if result.pdb_file else None,
            error_message=result.error_message,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=ProteinAnalyzeResponse)
async def analyze_prediction(job_id: str):
    """
    分析预测结果质量
    """
    try:
        client = get_client()
        result = await client.get_prediction(job_id)
        
        if not result or result.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Prediction not completed")
        
        analysis = analyze_structure(result)
        
        return ProteinAnalyzeResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualize/{job_id}")
async def visualize_structure(job_id: str, format: str = "svg"):
    """
    生成蛋白质结构可视化
    
    支持的格式:
    - svg: SVG 图像
    - html: 交互式 HTML 查看器
    - json: 结构化数据
    """
    try:
        client = get_client()
        result = await client.get_prediction(job_id)
        
        if not result or result.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Prediction not completed")
        
        if not result.pdb_file:
            raise HTTPException(status_code=404, detail="PDB file not available")
        
        # 创建可视化
        visualizer = ProteinVisualizer()
        visualizer.parse_pdb(result.pdb_file)
        
        if result.confidence_scores:
            visualizer.set_confidence_scores(result.confidence_scores)
        
        if format == "svg":
            svg_content = visualizer.generate_svg()
            return Response(content=svg_content, media_type="image/svg+xml")
        
        elif format == "json":
            data = visualizer.export_data("/tmp/structure.json")
            return Response(content=str(data), media_type="application/json")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-and-visualize")
async def predict_and_visualize(request: ProteinPredictRequest):
    """
    一键预测并生成可视化
    
    返回:
    - 预测结果
    - SVG 可视化
    - 质量分析
    """
    try:
        client = get_client()
        
        # 预测
        model = PredictionModel(request.model) if request.model in [m.value for m in PredictionModel] else PredictionModel.ESMFOLD
        pred_request = PredictionRequest(
            sequence=request.sequence,
            model=model,
            return_confidence=True,
        )
        
        result = await client.submit_prediction(pred_request)
        
        if result.status != JobStatus.COMPLETED:
            return {
                'success': False,
                'error': 'Prediction failed',
                'message': result.error_message,
            }
        
        # 可视化
        visualizer = ProteinVisualizer()
        visualizer.parse_pdb(result.pdb_file)
        if result.confidence_scores:
            visualizer.set_confidence_scores(result.confidence_scores)
        
        svg = visualizer.generate_svg()
        analysis = analyze_structure(result)
        
        return {
            'success': True,
            'prediction': {
                'job_id': result.job_id,
                'plddt_score': result.plddt_score,
                'processing_time': result.processing_time,
            },
            'analysis': analysis,
            'visualization': svg[:500] + '...' if len(svg) > 500 else svg,  # 截断 SVG
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }
