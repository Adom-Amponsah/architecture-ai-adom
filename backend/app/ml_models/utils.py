import networkx as nx
import torch
from torch_geometric.utils import from_networkx
from typing import Dict, Any

# Room Types mapping for encoding (Must match training)
ROOM_TYPES = {
    "living_room": 0,
    "kitchen": 1,
    "bedroom": 2,
    "bathroom": 3,
    "balcony": 4,
    "entrance": 5,
    "dining_room": 6,
    "study": 7,
    "storage": 8,
    "other": 9
}

def convert_nx_to_pyg_data(G: nx.Graph):
    """
    Convert NetworkX graph (from GraphBuilder) to PyTorch Geometric Data object
    compatible with the trained GNN encoder.
    """
    # 1. Ensure node attributes match training expectations
    # Training expects: 'type_idx' and 'area'
    
    for node_id, data in G.nodes(data=True):
        # Map string type to index
        r_type = data.get("type", "other")
        # Handle potential mismatch in naming conventions if any
        if r_type not in ROOM_TYPES:
            r_type = "other"
        
        data['type_idx'] = ROOM_TYPES[r_type]
        
        # Handle area (normalize as in training)
        # Training used: area_norm = area / 50.0
        # If min/max area is provided, use average, otherwise default
        min_area = data.get("min_area")
        max_area = data.get("max_area")
        
        if min_area and max_area:
            area = (min_area + max_area) / 2.0
        elif min_area:
            area = min_area
        else:
            area = 15.0 # Default
            
        data['area'] = area

    # 2. Build Feature Matrix x
    x = []
    # Note: G.nodes(data=True) order is preserved by from_networkx usually, 
    # but let's be careful. from_networkx uses canonical ordering if not specified.
    # It relies on list(G.nodes()).
    
    nodes_list = list(G.nodes(data=True))
    
    for node in nodes_list:
        type_idx = node[1]['type_idx']
        one_hot = [0] * len(ROOM_TYPES)
        one_hot[type_idx] = 1
        
        area_norm = node[1]['area'] / 50.0 
        x.append(one_hot + [area_norm])
        
    x = torch.tensor(x, dtype=torch.float)
    
    # 3. Convert to PyG
    # We must ensure from_networkx follows the same node order
    # It does not automatically align with our 'x' list if we just iterate G.nodes().
    # We should probably assign features to the graph first or be explicit.
    
    # Safer approach:
    # Assign 'x' attribute to nodes then use from_networkx? 
    # Or just rely on standard behavior: from_networkx iterates G.nodes()
    
    data = from_networkx(G)
    data.x = x
    
    return data
