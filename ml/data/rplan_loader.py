import os
import json
import numpy as np
import networkx as nx
import torch
from torch_geometric.utils import from_networkx
from typing import List, Dict, Tuple, Optional
import random

# Room Types mapping for encoding
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

class RPlanLoader:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path
        self.room_types = ROOM_TYPES
        
    def generate_synthetic_graph(self, num_rooms: int = None) -> nx.Graph:
        """
        Generates a synthetic architectural constraint graph for testing/training 
        without the full RPLAN dataset.
        """
        if num_rooms is None:
            num_rooms = random.randint(3, 8)
            
        G = nx.Graph()
        
        # 1. Create Nodes (Rooms)
        # Always have at least one living room and entrance for realism
        room_types_list = list(self.room_types.keys())
        
        # Room 0: Entrance
        G.add_node(0, room_type="entrance", type_idx=self.room_types["entrance"], area=random.uniform(3, 8))
        
        # Room 1: Living Room
        G.add_node(1, room_type="living_room", type_idx=self.room_types["living_room"], area=random.uniform(15, 30))
        
        # Connect Entrance to Living Room
        G.add_edge(0, 1, weight=1.0)
        
        # Add other rooms
        for i in range(2, num_rooms):
            rt = random.choice(room_types_list)
            # Simple heuristic: connect to living room or a previous room
            target = random.randint(1, i-1)
            
            G.add_node(i, room_type=rt, type_idx=self.room_types[rt], area=random.uniform(5, 20))
            G.add_edge(i, target, weight=1.0)
            
            # Maybe add another connection (cycle)
            if random.random() > 0.7:
                target2 = random.randint(1, i-1)
                if target2 != target:
                    G.add_edge(i, target2, weight=1.0)
                    
        return G

    def graph_to_pyg_data(self, G: nx.Graph):
        """
        Convert NetworkX graph to PyTorch Geometric Data object.
        Feature vector per node: [one_hot_type(10), area(1)] = 11 dims
        """
        # Node Features
        x = []
        for node in G.nodes(data=True):
            # One-hot encode room type
            type_idx = node[1]['type_idx']
            one_hot = [0] * len(self.room_types)
            one_hot[type_idx] = 1
            
            # Append Area (normalized roughly)
            area_norm = node[1]['area'] / 50.0 
            
            x.append(one_hot + [area_norm])
            
        x = torch.tensor(x, dtype=torch.float)
        
        # Edge Index
        data = from_networkx(G)
        data.x = x
        
        return data

    def get_dataloader(self, batch_size=32, num_samples=1000):
        """
        Returns a list of PyG Data objects (simplified loader)
        """
        dataset = []
        for _ in range(num_samples):
            G = self.generate_synthetic_graph()
            data = self.graph_to_pyg_data(G)
            dataset.append(data)
        
        from torch_geometric.loader import DataLoader
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)

if __name__ == "__main__":
    loader = RPlanLoader()
    G = loader.generate_synthetic_graph()
    print(f"Generated Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    data = loader.graph_to_pyg_data(G)
    print(f"PyG Data: {data}")
    print(f"Node Features shape: {data.x.shape}")

