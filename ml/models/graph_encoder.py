import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool

class ConstraintGraphEncoder(nn.Module):
    """
    Graph Neural Network to encode the architectural constraint graph 
    into a latent vector representation.
    """
    def __init__(self, node_dim=64, hidden_dim=128, out_dim=256, heads=4):
        super(ConstraintGraphEncoder, self).__init__()
        
        self.node_embedding = nn.Linear(node_dim, hidden_dim)
        
        # Graph Attention Layers
        self.gat1 = GATConv(hidden_dim, hidden_dim, heads=heads, concat=True)
        self.gat2 = GATConv(hidden_dim * heads, hidden_dim, heads=1, concat=False)
        
        # Output projection
        self.fc_out = nn.Linear(hidden_dim, out_dim)
        
    def forward(self, x, edge_index, edge_attr=None, batch=None):
        # x: Node features [num_nodes, node_dim]
        # edge_index: Graph connectivity [2, num_edges]
        
        x = F.relu(self.node_embedding(x))
        
        # GAT Layers
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.gat1(x, edge_index)
        x = F.elu(x)
        
        x = F.dropout(x, p=0.2, training=self.training)
        x = self.gat2(x, edge_index)
        x = F.elu(x)
        
        # Global Pooling (get graph-level embedding)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)
            
        x_graph = global_mean_pool(x, batch)
        
        # Final projection
        out = self.fc_out(x_graph)
        return out

if __name__ == "__main__":
    # Test instantiation
    model = ConstraintGraphEncoder(node_dim=10) # 10 input features per node
    print(model)
    print("Model initialized successfully")
