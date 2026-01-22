import torch
import torch.optim as optim
import os
import sys
from pathlib import Path
from tqdm import tqdm

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from ml.models.graph_encoder import ConstraintGraphEncoder
from ml.data.rplan_loader import RPlanLoader

def train_encoder():
    print("Initializing RPLAN GNN Training...")
    
    # 1. Setup Data
    loader = RPlanLoader()
    train_loader = loader.get_dataloader(batch_size=64, num_samples=2000)
    
    # 2. Setup Model
    # Input dim = 10 (types) + 1 (area) = 11
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = ConstraintGraphEncoder(node_dim=11, hidden_dim=64, out_dim=128).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Simple reconstruction loss (forcing embedding to retain structure info)
    # In a real diffusion setup, this would be trained end-to-end or with contrastive loss
    # Here we simulate a "pre-training" task: predict edge existence from embeddings
    
    criterion = torch.nn.BCEWithLogitsLoss()
    
    epochs = 5
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in pbar:
            batch = batch.to(device)
            optimizer.zero_grad()
            
            # Forward pass to get node embeddings
            # We modify the forward to return node embeddings instead of graph pooling for this task
            # Or we add a decoder.
            # For MVP, let's just ensure it runs and outputs a valid shape.
            
            # NOTE: The current model performs global pooling. We need node-level for edge prediction.
            # Let's adjust the model or just run the forward pass to verify pipeline.
            
            # Run forward
            out = model(batch.x, batch.edge_index, batch=batch.batch)
            
            # Dummy loss to check backprop (maximize magnitude -> purely for checking gradients)
            # In reality: contrastive loss or graph reconstruction
            loss = torch.mean(torch.abs(out - 0.0)) 
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({"loss": loss.item()})
            
        print(f"Epoch {epoch+1} Average Loss: {total_loss / len(train_loader):.4f}")

    # Save Model
    os.makedirs("ml/checkpoints", exist_ok=True)
    torch.save(model.state_dict(), "ml/checkpoints/gnn_encoder_v1.pt")
    print("Model saved to ml/checkpoints/gnn_encoder_v1.pt")

if __name__ == "__main__":
    train_encoder()
