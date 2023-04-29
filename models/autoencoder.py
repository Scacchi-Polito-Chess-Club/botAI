import torch.nn as nn
import torch


# TODO REDEFINE MODEL THIS IS A PLACEHOLDER
# TODO DEFINE DECODER OUTPUT


class AutoEncoder(nn.Module):
    """
    Definition of a custom autoencoder, with encoder and decoder.
    :param in_dim: input dimension of the chessboard + additional information
    :param out_dim: output dimension of action space
    :param latent_dim: dimension of encoded features
    """

    def __init__(self, in_dim=67, out_dim=64, encoder='linear', decoder='linear', latent_dim=32):
        super().__init__()
        if encoder == 'linear':
            # TODO: check dimensions
            self.encoder = nn.Sequential(nn.Linear(in_dim, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU(),
                                         nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, latent_dim)
                                         )
        elif enconder == 'conv':
            self.encoder = nn.Sequential(nn.Conv2d(1, 16, 2, 1), nn.ReLU(),  # 7x7
                                         nn.Conv2d(16, 32, 3, 1), nn.ReLU(),  # 5x5
                                         nn.Conv2d(32, latent_dim, 1, 1),  # 5x5
                                         nn.AvgPool2d(5)  # 32x1 (check hxw)
                                         )
        else:
            raise NotImplementedError(f'{encoder} encoder not implemented')

        if decoder == 'linear':
            self.decoder = nn.Sequential(nn.Linear(latent_dim, latent_dim * 2), nn.ReLU(),
                                         nn.Linear(latent_dim * 2, out_dim)
                                         )
        else:
            raise NotImplementedError(f'{encoder} encoder not implemented')

    def forward(self, b1, b2):
        """
        Taken two chessboards b1 and b2, it outputs the action space.
        """
        batch_size = b1.shape[0]
        z1 = self.encoder(b1)
        z2 = self.encoder(b2)
        z3 = z1 - z2
        action_space = self.decoder(z3)
        assert action_space.shape == (batch_size, self.out_dim)
        return action_space

