from models.autoencoder import AutoEncoder


def get_autoencoder(encoder: str, decoder: str, latent_dim: int) -> nn.Module:
    return AutoEncoder()
