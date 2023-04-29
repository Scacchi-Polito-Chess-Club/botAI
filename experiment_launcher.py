import argparse

import torch.optim

import games_from_dataset as gd
import torch.nn as nn
import torch.utils.data as data

from utils.utils_autoencoder import get_autoencoder


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=str, default=None, help='checkpoint path')
    parser.add_argument('--device', type=str, default='cpu', help='device where to run model, cpu or cuda')
    parser.add_argument('--wandb', type=str, default=None, help='wandb_logging')

    # EXPERIMENT ARGS
    parser.add_argument('--exp', type=str, default='train', help='type of experiment, train or test')
    parser.add_argument('--epoch', type=int, default=50, help='number of epochs')
    parser.add_argument('--optimizer', type=str, default='sgd', help='type of optimizer')
    parser.add_argument('--scheduler', type=str, default='exp', help='type of scheduler')
    parser.add_argument('--lr', type=float, default=1e-3, help='learning rate')
    parser.add_argument('--eval_step', type=int, default=10, help='rate of evaluation steps')

    # DATA ARGS
    parser.add_argument('--data', type=str, default='./dataset.pgn', help='path to dataset')
    parser.add_argument('--n_games', type=int, default=10, help='number of games to be loaded')

    # DATALOADER ARGS
    parser.add_argument('--num_workers', type=int, default=0, help='number of workers for dataloader')
    parser.add_argument('--bs', type=int, default=8, help='batch size')

    # ENCODER ARGS
    parser.add_argument('--encoder', type=str, default='conv', help='type of encoder')
    parser.add_argument('--decoder', type=str, default='linear', help='type of decoder')
    parser.add_argument('--latent_dim', type=int, default=16, help='dimension of the latent space')

    return parser.parse_args()


def get_optimizer(model: nn.Module, type: str, lr: float):
    if type == 'sgd':
        optim = torch.optim.SGD(model.parameters(), lr=lr)
    else:
        raise NotImplementedError(f'{type} optimizer not implemented yet')
    # ADD HERE NEW OPTIMIZERS
    return optim


def get_scheduler(optim: torch.optim.lr_scheduler, type: str):
    if type == 'exp':
        scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer=optim, gamma=0.95)
    else:
        raise NotImplementedError(f'{type} scheduler not implemented yet')
    # ADD HERE NEW SCHEDULERS
    return scheduler


def get_critereon():
    # TODO DEFINE LOSS
    return lambda x, y: x


@torch.no_grad()
def test(model, test_data, args):
    device = args.device
    eval_critereon = get_critereon(type)
    tot_stat = 0
    for (b1, b2), move_gt in test_data:
        b1, b2, move_gt = b1.to(device), b2.to(device), move_gt.to(device)
        move = model(b1, b2)
        crit_stat = eval_critereon(move)
        tot_stat += crit_stat
    return tot_stat


def train(model: nn.Module, train_data: data.DataLoader, val_data: data.DataLoader, args):
    device = args.device
    model = model.to(device)
    optim = get_optimizer(model, args.optimizer, args.lr)
    sched = get_scheduler(optim, type=args.scheduler)
    critereon = get_critereon()

    if args.resume is not None:
        raise NotImplementedError()

    init_epoch = 0
    for epoch in range(init_epoch, args.epoch):
        for (b1, b2), move_gt in train_data:
            b1, b2 = b1.to(device).float(), b2.to(device).float()
            optim.zero_grad()
            move = model(b1, b2)
            loss = critereon(move, move_gt)
            loss.backward()
            optim.step()
        sched.step()

        if epoch % args.eval_step == 0:
            eval_stats = test(model, val_data)
            print(eval_stats)

    return model


def main(args):
    """
    Start a training or experiment run
    :param args: arguments from argparse
    :return: None
    """

    if args.wandb is not None:
        raise NotImplementedError('logging not implemented yet')
    model = get_autoencoder(args.encoder, args.decoder, args.latent_dim)
    train_data, val_data, test_data = gd.get_dataloader(fname=args.data,
                                                        num_workers=args.num_workers,
                                                        batch_size=args.bs,
                                                        board_transform=gd.board_to_array2)

    if args.exp == 'train':
        train(model, train_data, val_data, args)
        test(model)
    elif args.exp == 'test':
        ckpt = torch.load(args.resume)
        model.load_state_dict(ckpt['model_state_dict'], strict=True)
        test(model)


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
