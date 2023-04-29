import torch.nn as nn
import torch


# TODO DEFINE DECODER OUTPUT


class AutoEncoder(nn.Module):

    def __init__(self, config: dict):
        super().__init__()
        self.in_dim = config['encoder']['input_dim']
        self.lat_dim = config['encoder']['laten_dim']
        self.out_dim = config['decoder']['output_dim']
        self.encoder = self.build_encoder(config)
        self.decoder = self.build_decoder(config)

    def build_encoder(self, config):
        if config['encoder']['type'] == 'linear':
            # building encoder with Linear layers; it returns a number of features equal to lat_dim
            encoder = nn.Sequential(nn.Linear(self.in_dim, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU(),
                                    nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, self.lat_dim)
                                    )
        elif config['encoder']['type'] == 'conv':
            # TODO: check dimensions of the matrix
            # building encoder with Convolutional Layers; THE INPUT MUST BE A MATRIX
            encoder = nn.Sequential(nn.Conv2d(1, 16, 2, 1), nn.ReLU(),  # 7x7
                                    nn.Conv2d(16, 32, 3, 1), nn.ReLU(),  # 5x5
                                    nn.Conv2d(32, self.lat_dim, 1, 1),  # 5x5
                                    nn.AvgPool2d(5)  # 32x1 (check hxw)
                                    )
        else:
            raise NotImplementedError(f'Encoder not implemented')

        return encoder

    def build_decoder(self, config):
        if config['decoder']['type'] == 'linear':
            # TODO: check action_space dimensions
            # building decoder with Linear Layers; it returns a number of moves equal to out_dim
            decoder = nn.Sequential(nn.Linear(self.lat_dim, self.lat_dim * 2), nn.ReLU(),
                                    nn.Linear(self.lat_dim * 2, self.out_dim)
                                    )
        else:
            raise NotImplementedError(f'Decoder not implemented')

        return decoder

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
