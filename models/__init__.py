import torch.nn as nn
import torch

# TODO REDEFINE MODEL THIS IS A PLACEHOLDER
# TODO DEFINE DECODER OUTPUT

class AutoEncoder(nn.Module):
    def __init__(self, in_dim=128, out_dim=64, encoder='dumb', decoder='dumb', latent_dim=32):
        super().__init__()
        if encoder == 'dumb':
            self.encoder = nn.Linear(in_dim, latent_dim)
        else:
            raise NotImplementedError(f'{encoder} encoder not implemented')
        if decoder == 'dumb':
            self.decoder = nn.Linear(latent_dim, out_dim)
        else:
            raise NotImplementedError(f'{encoder} encoder not implemented')

    def forward(self, b1, b2):
        b = torch.cat([b1, b2], axis=1)
        z = self.encoder(b)
        m = self.decoder(z)
        return m


def get_model(encoder: str, decoder: str, latent_dim: int) -> nn.Module:
    return AutoEncoder()
