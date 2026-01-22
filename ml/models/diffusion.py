import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SinusoidalPositionEmbeddings(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, time):
        device = time.device
        half_dim = self.dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = time[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        return embeddings

class LayoutDiffusionModel(nn.Module):
    """
    Conditional Diffusion Model for Layout Generation.
    Predicts noise added to the layout representation at timestep t,
    conditioned on the constraint graph embedding.
    """
    def __init__(self, input_dim=4, condition_dim=256, time_dim=64, hidden_dim=256):
        super().__init__()
        # input_dim: 4 for [x, y, w, h] per room (simplified) or flattened vector
        
        self.time_mlp = nn.Sequential(
            SinusoidalPositionEmbeddings(time_dim),
            nn.Linear(time_dim, time_dim),
            nn.ReLU()
        )
        
        self.cond_mlp = nn.Sequential(
            nn.Linear(condition_dim, time_dim),
            nn.ReLU()
        )
        
        # Denoising MLP (Simple Residual Block style)
        self.net = nn.Sequential(
            nn.Linear(input_dim + time_dim * 2, hidden_dim), # Input + Time + Condition
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )

    def forward(self, x, t, condition):
        # x: Noisy layout [batch, input_dim]
        # t: Timestep [batch]
        # condition: Graph embedding [batch, condition_dim]
        
        t_emb = self.time_mlp(t)
        c_emb = self.cond_mlp(condition)
        
        # Concatenate input, time embedding, and condition embedding
        # (Broadcasting c_emb and t_emb if necessary, but here assuming dense layers handle it)
        inp = torch.cat([x, t_emb, c_emb], dim=1)
        
        return self.net(inp)

class DiffusionSampler:
    def __init__(self, model, beta_start=1e-4, beta_end=0.02, n_steps=1000, device="cpu"):
        self.model = model
        self.n_steps = n_steps
        self.device = device
        
        self.betas = torch.linspace(beta_start, beta_end, n_steps).to(device)
        self.alphas = 1. - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, axis=0)
        self.alphas_cumprod_prev = F.pad(self.alphas_cumprod[:-1], (1, 0), value=1.0)
        
        self.sqrt_recip_alphas = torch.sqrt(1.0 / self.alphas)
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1. - self.alphas_cumprod)
        self.posterior_variance = self.betas * (1. - self.alphas_cumprod_prev) / (1. - self.alphas_cumprod)

    def q_sample(self, x_0, t, noise=None):
        """
        Forward diffusion process: q(x_t | x_0)
        Add noise to the data at timestep t.
        """
        if noise is None:
            noise = torch.randn_like(x_0)
            
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t][:, None]
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t][:, None]
        
        return sqrt_alphas_cumprod_t * x_0 + sqrt_one_minus_alphas_cumprod_t * noise

    @torch.no_grad()
    def p_sample(self, x, t, t_index, condition):
        """
        Reverse diffusion process: p(x_{t-1} | x_t)
        """
        betas_t = self.betas[t]
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t]
        sqrt_recip_alphas_t = self.sqrt_recip_alphas[t]
        
        # Model predicts noise
        model_mean = sqrt_recip_alphas_t * (
            x - betas_t * self.model(x, t, condition) / sqrt_one_minus_alphas_cumprod_t
        )
        
        if t_index == 0:
            return model_mean
        else:
            posterior_variance_t = self.posterior_variance[t]
            noise = torch.randn_like(x)
            return model_mean + torch.sqrt(posterior_variance_t) * noise

    @torch.no_grad()
    def sample(self, condition, shape):
        b = shape[0]
        # Start from pure noise
        img = torch.randn(shape, device=self.device)
        
        for i in reversed(range(0, self.n_steps)):
            t = torch.full((b,), i, device=self.device, dtype=torch.long)
            img = self.p_sample(img, t, i, condition)
            
        return img
