import os
import networkx as nx
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
from app.ml_models.utils import convert_nx_to_pyg_data

try:
    import torch
    from app.ml_models.graph_encoder import ConstraintGraphEncoder
    from app.ml_models.diffusion import LayoutDiffusionModel, DiffusionSampler
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("WARNING: PyTorch not found. ML inference will be disabled.")

class MLInferenceService:
    def __init__(self):
        self.device = 'cpu'
        if TORCH_AVAILABLE:
            self.device = torch.device('cpu') # Inference on CPU is fine for MVP
        
        self.base_path = Path(__file__).resolve().parent.parent / "ml_models" / "checkpoints"
        
        self.gnn = None
        self.diffusion = None
        self.sampler = None
        self.models_loaded = False
        
    def load_models(self):
        if not TORCH_AVAILABLE:
            print("Cannot load models: PyTorch is not available.")
            return

        if self.models_loaded:
            return

        print(f"Loading ML Models from {self.base_path}...")
        
        # 1. Load GNN
        self.gnn = ConstraintGraphEncoder(node_dim=11, hidden_dim=64, out_dim=128).to(self.device)
        gnn_path = self.base_path / "gnn_encoder_v1.pt"
        if gnn_path.exists():
            self.gnn.load_state_dict(torch.load(gnn_path, map_location=self.device))
            self.gnn.eval()
            print("GNN Encoder loaded.")
        else:
            print(f"WARNING: GNN Checkpoint not found at {gnn_path}")

        # 2. Load Diffusion
        # Fixed dimensions from training
        LAYOUT_DIM = 32 
        self.diffusion = LayoutDiffusionModel(input_dim=LAYOUT_DIM, condition_dim=128).to(self.device)
        diff_path = self.base_path / "diffusion_v1.pt"
        if diff_path.exists():
            self.diffusion.load_state_dict(torch.load(diff_path, map_location=self.device))
            self.diffusion.eval()
            print("Diffusion Model loaded.")
        else:
             print(f"WARNING: Diffusion Checkpoint not found at {diff_path}")
            
        self.sampler = DiffusionSampler(self.diffusion, device=self.device, n_steps=50) # Fewer steps for inference speed
        self.models_loaded = True

    def generate_layout(self, graph_data: dict) -> Dict[str, Any]:
        """
        Run full inference pipeline: Graph Dict -> NetworkX -> PyG -> GNN -> Diffusion -> SVG & Geometry
        """
        if not TORCH_AVAILABLE:
            raise RuntimeError("ML Inference is unavailable because PyTorch is not installed.")

        if not self.models_loaded:
            self.load_models()
            
        # 1. Reconstruct NetworkX Graph from JSON dict
        G = nx.node_link_graph(graph_data)
        
        # 2. Convert to PyG Data
        pyg_data = convert_nx_to_pyg_data(G).to(self.device)
        
        # 3. Encode Graph
        with torch.no_grad():
            # batch vector of zeros since size is 1
            batch = torch.zeros(pyg_data.num_nodes, dtype=torch.long, device=self.device)
            condition = self.gnn(pyg_data.x, pyg_data.edge_index, batch=batch)
        
        # 4. Run Diffusion Sampling
        # Output shape: [1, 32] -> 8 rooms * 4 coords
        with torch.no_grad():
            layout_vector = self.sampler.sample(condition, (1, 32))
            
        # 5. Decode Vector to Geometry
        geometry_data = self._vector_to_geometry(layout_vector[0].cpu().numpy(), G)
        
        # 6. Generate SVG from Geometry
        svg_output = self._geometry_to_svg(geometry_data)
        
        return {
            "svg": svg_output,
            "geometry": geometry_data
        }

    def _vector_to_geometry(self, layout_vec: np.ndarray, G: nx.Graph) -> List[Dict[str, Any]]:
        """
        Convert raw layout vector to structured geometry list.
        """
        scale = 5.0 
        offset_x = 400
        offset_y = 300
        
        nodes = list(G.nodes(data=True))
        num_rooms = len(nodes)
        
        rooms_geometry = []
        
        for i in range(min(num_rooms, 8)):
            # Extract box
            base_idx = i * 4
            x_raw, y_raw, w_raw, h_raw = layout_vec[base_idx:base_idx+4]
            
            # Dimensions
            w = abs(w_raw) * scale + 20 
            h = abs(h_raw) * scale + 20
            
            # Position (Center)
            cx = x_raw * scale + offset_x
            cy = y_raw * scale + offset_y
            
            # Top-Left for SVG/2D
            x = cx - (w/2)
            y = cy - (h/2)
            
            room_data = nodes[i][1]
            
            rooms_geometry.append({
                "id": nodes[i][0],
                "name": room_data.get('label', 'Room'),
                "type": room_data.get('type', 'other'),
                "x": float(x),
                "y": float(y),
                "width": float(w),
                "height": float(h),
                "center_x": float(cx),
                "center_y": float(cy)
            })
            
        return rooms_geometry

    def _geometry_to_svg(self, geometry: List[Dict[str, Any]]) -> str:
        """
        Render structured geometry to SVG.
        """
        svg_parts = [
            f'<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" style="background-color: #f0f0f0;">'
        ]
        
        for room in geometry:
            x, y, w, h = room['x'], room['y'], room['width'], room['height']
            color = self._get_room_color(room['type'])
            
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="black" stroke-width="2" fill-opacity="0.7" />'
            )
            svg_parts.append(
                f'<text x="{x + w/2}" y="{y + h/2}" font-family="Arial" font-size="12" text-anchor="middle" fill="black">{room["name"]}</text>'
            )
            
        svg_parts.append('</svg>')
        return "".join(svg_parts)

    def _vector_to_svg(self, layout_vec: np.ndarray, G: nx.Graph) -> str:
        # Legacy wrapper if needed, but we used it internally before.
        # Can be removed or redirected.
        geom = self._vector_to_geometry(layout_vec, G)
        return self._geometry_to_svg(geom)


    def _get_room_color(self, room_type: str) -> str:
        colors = {
            "living_room": "#FFCC80", # Orange
            "kitchen": "#EF9A9A",    # Red
            "bedroom": "#90CAF9",    # Blue
            "bathroom": "#81C784",   # Green
            "balcony": "#B0BEC5",    # Grey
            "entrance": "#FFF59D",   # Yellow
            "corridor": "#E0E0E0",
            "other": "#CE93D8"       # Purple
        }
        return colors.get(room_type, "#FFFFFF")

ml_service = MLInferenceService()
