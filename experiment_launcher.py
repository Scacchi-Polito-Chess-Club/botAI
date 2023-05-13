import games_from_dataset as gd
import torch.optim
import torch.nn as nn
import torch.utils.data as data
from utils.utils_model import *


@torch.no_grad()
def test(model, test_data, config):
    device = config['setup_args']['device']
    eval_func = get_loss_func(config['exp_args']['loss'])
    tot_stat = 0
    for (b1, b2), move_gt in test_data:
        b1, b2, move_gt = b1.to(device), b2.to(device), move_gt.to(device)
        move = model(b1, b2)
        eval_stat = eval_func(move, move_gt)
        tot_stat += eval_stat
    return tot_stat


def train(model: nn.Module, train_data: data.DataLoader, val_data: data.DataLoader, config):
    device = config['setup_args']['device']
    model = model.to(device)
    optim = get_optimizer(model, config['exp_args']['optimizer'].lower(), config['exp_args']['lr'])
    sched = get_scheduler(optim, type=config['exp_args']['scheduler'])
    loss_func = get_loss_func(config['exp_args']['loss'])

    if config['setup_args']['resume'] is not None:
        raise NotImplementedError()

    init_epoch = 0
    for epoch in range(init_epoch, config['exp_args']['epoch']):
        for (b1, b2), move_gt in train_data:
            b1, b2 = b1.to(device).float(), b2.to(device).float()
            optim.zero_grad()
            move = model(b1, b2)
            loss = loss_func(move, move_gt)
            loss.backward()
            optim.step()
        sched.step()

        if epoch % args.eval_step == 0:
            eval_stats = test(model, val_data)
            print(eval_stats)

    return model


