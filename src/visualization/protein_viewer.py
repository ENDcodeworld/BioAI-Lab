"""
蛋白质可视化模块
支持 PDB 文件渲染、3D 结构展示、置信度热力图
"""
import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Atom:
    """原子坐标"""
    atom_id: int
    atom_name: str
    residue_name: str
    chain: str
    residue_id: int
    x: float
    y: float
    z: float
    occupancy: float
    temp_factor: float
    element: str


@dataclass
class Residue:
    """氨基酸残基"""
    residue_id: int
    residue_name: str
    chain: str
    atoms: List[Atom]
    ca_coordinates: Optional[Tuple[float, float, float]] = None


@dataclass
class ProteinStructure:
    """蛋白质结构"""
    title: str
    residues: List[Residue]
    num_chains: int
    num_residues: int
    num_atoms: int
    metadata: Dict


class ProteinVisualizer:
    """
    蛋白质结构可视化器
    生成 Web 友好的可视化数据
    """
    
    def __init__(self):
        self.structure: Optional[ProteinStructure] = None
        self.confidence_scores: Optional[List[float]] = None
    
    def parse_pdb(self, pdb_content: str) -> ProteinStructure:
        """
        解析 PDB 文件内容
        
        Args:
            pdb_content: PDB 文件文本内容
        
        Returns:
            ProteinStructure: 解析后的结构
        """
        atoms: List[Atom] = []
        residues_dict: Dict[Tuple[str, int], Residue] = {}
        title = "Unknown Structure"
        
        for line in pdb_content.split('\n'):
            if line.startswith('TITLE'):
                title = line[10:].strip()
            elif line.startswith('ATOM'):
                try:
                    atom = self._parse_atom_line(line)
                    if atom:
                        atoms.append(atom)
                        
                        # 组织残基
                        key = (atom.chain, atom.residue_id)
                        if key not in residues_dict:
                            residues_dict[key] = Residue(
                                residue_id=atom.residue_id,
                                residue_name=atom.residue_name,
                                chain=atom.chain,
                                atoms=[]
                            )
                        residues_dict[key].atoms.append(atom)
                        
                        # 记录 CA 原子坐标
                        if atom.atom_name == 'CA':
                            residues_dict[key].ca_coordinates = (atom.x, atom.y, atom.z)
                except (ValueError, IndexError):
                    continue
        
        # 转换为列表并排序
        residues = sorted(residues_dict.values(), key=lambda r: r.residue_id)
        
        # 计算链数
        chains = set(r.chain for r in residues)
        
        self.structure = ProteinStructure(
            title=title,
            residues=residues,
            num_chains=len(chains),
            num_residues=len(residues),
            num_atoms=len(atoms),
            metadata={
                'parsed_successfully': True,
            }
        )
        
        return self.structure
    
    def _parse_atom_line(self, line: str) -> Optional[Atom]:
        """解析 PDB ATOM 记录行"""
        try:
            return Atom(
                atom_id=int(line[6:11]),
                atom_name=line[12:16].strip(),
                residue_name=line[17:20].strip(),
                chain=line[21] if len(line) > 21 else 'A',
                residue_id=int(line[22:26]),
                x=float(line[30:38]),
                y=float(line[38:46]),
                z=float(line[46:54]),
                occupancy=float(line[54:60]) if len(line) > 60 else 1.0,
                temp_factor=float(line[60:66]) if len(line) > 66 else 0.0,
                element=line[76:78].strip() if len(line) > 76 else 'C',
            )
        except (ValueError, IndexError):
            return None
    
    def set_confidence_scores(self, scores: List[float]):
        """设置置信度分数 (用于热力图着色)"""
        if self.structure and len(scores) == len(self.structure.residues):
            self.confidence_scores = scores
    
    def generate_svg(self, 
                    width: int = 800,
                    height: int = 600,
                    style: str = "cartoon") -> str:
        """
        生成 SVG 可视化
        
        Args:
            width: 图像宽度
            height: 图像高度
            style: 渲染风格 (cartoon, backbone, spheres)
        
        Returns:
            SVG 字符串
        """
        if not self.structure or not self.structure.residues:
            return self._empty_svg(width, height)
        
        # 计算边界框
        coords = [r.ca_coordinates for r in self.structure.residues if r.ca_coordinates]
        if not coords:
            return self._empty_svg(width, height)
        
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        z_coords = [c[2] for c in coords]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        min_z, max_z = min(z_coords), max(z_coords)
        
        # 归一化坐标到 SVG 空间
        def normalize(x, y, z):
            nx = (x - min_x) / (max_x - min_x + 0.001) * (width - 100) + 50
            ny = height - ((y - min_y) / (max_y - min_y + 0.001) * (height - 100) + 50)
            return nx, ny
        
        # 生成 SVG
        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'  <defs>',
            f'    <linearGradient id="confidenceGradient" x1="0%" y1="0%" x2="100%" y2="0%">',
            f'      <stop offset="0%" style="stop-color:blue;stop-opacity:1" />',
            f'      <stop offset="50%" style="stop-color:yellow;stop-opacity:1" />',
            f'      <stop offset="100%" style="stop-color:red;stop-opacity:1" />',
            f'    </linearGradient>',
            f'  </defs>',
            f'  <rect width="100%" height="100%" fill="white"/>',
            f'  <text x="{width//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">{self.structure.title}</text>',
        ]
        
        if style == "backbone" or style == "cartoon":
            # 绘制主链
            path_d = []
            colors = []
            
            for i, residue in enumerate(self.structure.residues):
                if residue.ca_coordinates:
                    x, y = normalize(*residue.ca_coordinates)
                    if i == 0:
                        path_d.append(f"M {x:.1f} {y:.1f}")
                    else:
                        path_d.append(f"L {x:.1f} {y:.1f}")
                    
                    # 根据置信度着色
                    if self.confidence_scores and i < len(self.confidence_scores):
                        score = self.confidence_scores[i]
                        color = self._score_to_color(score)
                        colors.append(color)
            
            if path_d:
                if colors and len(set(colors)) > 1:
                    # 多色主链
                    svg_lines.append(f'  <path d="{" ".join(path_d)}" fill="none" stroke="url(#confidenceGradient)" stroke-width="3" stroke-linecap="round"/>')
                else:
                    svg_lines.append(f'  <path d="{" ".join(path_d)}" fill="none" stroke="#3366CC" stroke-width="3" stroke-linecap="round"/>')
        
        if style == "spheres" or style == "cartoon":
            # 绘制 CA 原子球
            for i, residue in enumerate(self.structure.residues):
                if residue.ca_coordinates:
                    x, y = normalize(*residue.ca_coordinates)
                    
                    if self.confidence_scores and i < len(self.confidence_scores):
                        color = self._score_to_color(self.confidence_scores[i])
                    else:
                        color = "#3366CC"
                    
                    svg_lines.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" opacity="0.7"/>')
        
        # 添加图例
        svg_lines.extend([
            f'  <text x="{width - 150}" y="60" font-size="12">Confidence:</text>',
            f'  <rect x="{width - 150}" y="70" width="100" height="10" fill="url(#confidenceGradient)"/>',
            f'  <text x="{width - 150}" y="90" font-size="10">Low</text>',
            f'  <text x="{width - 80}" y="90" font-size="10">High</text>',
            f'  <text x="10" y="{height - 20}" font-size="11">Residues: {self.structure.num_residues} | Chains: {self.structure.num_chains}</text>',
            f'</svg>',
        ])
        
        return '\n'.join(svg_lines)
    
    def _score_to_color(self, score: float) -> str:
        """将置信度分数转换为颜色"""
        if score >= 70:
            return "#00AA00"  # 绿色 - 高置信度
        elif score >= 50:
            return "#FFAA00"  # 橙色 - 中置信度
        else:
            return "#FF0000"  # 红色 - 低置信度
    
    def _empty_svg(self, width: int, height: int) -> str:
        """生成空 SVG"""
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#f5f5f5"/>
  <text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="16" fill="#999">No structure data</text>
</svg>'''
    
    def generate_html_viewer(self, 
                            output_path: str,
                            title: str = "Protein Structure Viewer",
                            include_controls: bool = True) -> str:
        """
        生成完整的 HTML 查看器
        
        Args:
            output_path: 输出文件路径
            title: 页面标题
            include_controls: 是否包含交互控件
        
        Returns:
            HTML 文件路径
        """
        svg_content = self.generate_svg(800, 600)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        h1 {{
            margin-top: 0;
            color: #333;
        }}
        .viewer {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .structure-view {{
            flex: 1;
            min-width: 600px;
        }}
        .info-panel {{
            width: 300px;
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }}
        .stat {{
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-weight: 600;
            color: #666;
        }}
        .stat-value {{
            font-size: 1.2em;
            color: #333;
        }}
        .controls {{
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }}
        button {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
        }}
        button:hover {{
            background: #f0f0f0;
            border-color: #999;
        }}
        button.active {{
            background: #3366CC;
            color: white;
            border-color: #3366CC;
        }}
        .sequence-view {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .confidence-legend {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }}
        .gradient-bar {{
            flex: 1;
            height: 20px;
            background: linear-gradient(to right, blue, yellow, red);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 {title}</h1>
        
        <div class="viewer">
            <div class="structure-view">
                {svg_content}
                
                {'''<div class="controls">
                    <button class="style-btn active" data-style="cartoon">Cartoon</button>
                    <button class="style-btn" data-style="backbone">Backbone</button>
                    <button class="style-btn" data-style="spheres">Spheres</button>
                </div>''' if include_controls else ''}
            </div>
            
            <div class="info-panel">
                <h3>Structure Info</h3>
                <div class="stat">
                    <div class="stat-label">Residues</div>
                    <div class="stat-value">{self.structure.num_residues if self.structure else 0}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Chains</div>
                    <div class="stat-value">{self.structure.num_chains if self.structure else 0}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Atoms</div>
                    <div class="stat-value">{self.structure.num_atoms if self.structure else 0}</div>
                </div>
                
                <div class="confidence-legend">
                    <span>Confidence:</span>
                    <div class="gradient-bar"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666;">
                    <span>Low (0)</span>
                    <span>High (100)</span>
                </div>
            </div>
        </div>
        
        {self._generate_sequence_view() if self.structure else ''}
    </div>
    
    <script>
        document.querySelectorAll('.style-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                // In a full implementation, this would re-render the structure
                console.log('Switch to style:', btn.dataset.style);
            }});
        }});
    </script>
</body>
</html>'''
        
        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)
        
        return str(output_path)
    
    def _generate_sequence_view(self) -> str:
        """生成序列视图 HTML"""
        if not self.structure:
            return ""
        
        sequence = ''.join(self._residue_to_aa(r.residue_name) for r in self.structure.residues)
        
        # 添加置信度着色
        colored_seq = []
        for i, aa in enumerate(sequence):
            if self.confidence_scores and i < len(self.confidence_scores):
                score = self.confidence_scores[i]
                if score >= 70:
                    color = '#00aa00'
                elif score >= 50:
                    color = '#ffaa00'
                else:
                    color = '#ff0000'
                colored_seq.append(f'<span style="color: {color}">{aa}</span>')
            else:
                colored_seq.append(aa)
        
        return f'''
        <div class="sequence-view">
            <h3>Sequence</h3>
            <div>{"".join(colored_seq)}</div>
        </div>
        '''
    
    def _residue_to_aa(self, residue_name: str) -> str:
        """三字母残基名转单字母氨基酸代码"""
        mapping = {
            'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D',
            'CYS': 'C', 'GLN': 'Q', 'GLU': 'E', 'GLY': 'G',
            'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
            'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S',
            'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
        }
        return mapping.get(residue_name.upper(), 'X')
    
    def export_data(self, output_path: str) -> Dict:
        """导出结构化数据"""
        if not self.structure:
            return {}
        
        data = {
            'title': self.structure.title,
            'num_residues': self.structure.num_residues,
            'num_chains': self.structure.num_chains,
            'num_atoms': self.structure.num_atoms,
            'residues': [],
            'confidence_scores': self.confidence_scores,
        }
        
        for residue in self.structure.residues:
            residue_data = {
                'id': residue.residue_id,
                'name': residue.residue_name,
                'chain': residue.chain,
                'ca_coords': residue.ca_coordinates,
            }
            data['residues'].append(residue_data)
        
        # 写入 JSON
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2))
        
        return data


# 便捷函数
def visualize_pdb(pdb_content: str, 
                 output_dir: str = "./output",
                 confidence_scores: Optional[List[float]] = None) -> Dict[str, str]:
    """
    便捷函数：可视化 PDB 结构
    
    Returns:
        生成的文件路径字典
    """
    visualizer = ProteinVisualizer()
    visualizer.parse_pdb(pdb_content)
    
    if confidence_scores:
        visualizer.set_confidence_scores(confidence_scores)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {}
    
    # 生成 SVG
    svg_path = output_dir / "structure.svg"
    svg_path.write_text(visualizer.generate_svg())
    files['svg'] = str(svg_path)
    
    # 生成 HTML 查看器
    html_path = output_dir / "viewer.html"
    visualizer.generate_html_viewer(str(html_path))
    files['html'] = str(html_path)
    
    # 导出数据
    json_path = output_dir / "structure_data.json"
    visualizer.export_data(str(json_path))
    files['json'] = str(json_path)
    
    return files
