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
from ml.models.diffusion import LayoutDiffusionModel, DiffusionSampler
from ml.data.rplan_loader import RPlanLoader

def train_diffusion():
    print("Initializing Diffusion Model Training...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 1. Setup Data & Encoder
    loader = RPlanLoader()
    # Increased samples for diffusion
    train_loader = loader.get_dataloader(batch_size=32, num_samples=2000) 
    
    # Load Pre-trained GNN
    gnn = ConstraintGraphEncoder(node_dim=11, hidden_dim=64, out_dim=128).to(device)
    gnn_path = "ml/checkpoints/gnn_encoder_v1.pt"
    if os.path.exists(gnn_path):
        gnn.load_state_dict(torch.load(gnn_path, map_location=device))
        print("Loaded pre-trained GNN encoder")
    else:
        print("Warning: Pre-trained GNN not found, using random initialization")
    
    gnn.eval() # Freeze GNN for now
    
    # 2. Setup Diffusion Model
    # For this skeleton, let's assume we generate a fixed vector representing the layout
    # e.g. [GlobalWidth, GlobalHeight, LivingX, LivingY, ...] 
    # To keep it simple and dynamic, let's just model a fixed number of max rooms (e.g. 8) * 4 params [x,y,w,h] = 32
    LAYOUT_DIM = 32 
    
    model = LayoutDiffusionModel(input_dim=LAYOUT_DIM, condition_dim=128).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    sampler = DiffusionSampler(model, device=device)
    
    criterion = torch.nn.MSELoss()
    
    epochs = 5
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in pbar:
            batch = batch.to(device)
            optimizer.zero_grad()
            
            # 1. Get Condition Embedding from Graph
            with torch.no_grad():
                condition = gnn(batch.x, batch.edge_index, batch=batch.batch)
            
            # 2. Get "Real" Layout Data (Synthetic for now)
            # In a real scenario, this comes from the dataset
            # Here we generate random boxes as dummy ground truth
            batch_size = condition.size(0)
            x_0 = torch.rand(batch_size, LAYOUT_DIM).to(device) 
            
            # 3. Sample Timesteps
            t = torch.randint(0, sampler.n_steps, (batch_size,), device=device).long()
            
            # 4. Add Noise
            noise = torch.randn_like(x_0)
            x_t = sampler.q_sample(x_0, t, noise)
            
            # 5. Predict Noise
            predicted_noise = model(x_t, t, condition)
            
            # 6. Loss
            loss = criterion(predicted_noise, noise)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({"loss": loss.item()})
            
        print(f"Epoch {epoch+1} Average Loss: {total_loss / len(train_loader):.4f}")

    # Save Model
    os.makedirs("ml/checkpoints", exist_ok=True)
    torch.save(model.state_dict(), "ml/checkpoints/diffusion_v1.pt")
    print("Model saved to ml/checkpoints/diffusion_v1.pt")
    
    # Test Sampling
    print("Testing Generation...")
    model.eval()
    with torch.no_grad():
        # Get one condition
        sample_graph = next(iter(train_loader)).to(device)
        condition = gnn(sample_graph.x, sample_graph.edge_index, batch=sample_graph.batch)
        condition = condition[0:1] # Take first one
        
        generated_layout = sampler.sample(condition, (1, LAYOUT_DIM))
        print("Generated Layout Vector (First 4 values):", generated_layout[0][:4].cpu().numpy())

if __name__ == "__main__":
    train_diffusion()
