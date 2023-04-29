import torch.optim
import games_from_dataset as gd
import torch.nn as nn
import torch.utils.data as data


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
def test(model, test_data, config):
    device = config['setup_args']['device']
    eval_critereon = get_critereon(type)
    tot_stat = 0
    for (b1, b2), move_gt in test_data:
        b1, b2, move_gt = b1.to(device), b2.to(device), move_gt.to(device)
        move = model(b1, b2)
        crit_stat = eval_critereon(move)
        tot_stat += crit_stat
    return tot_stat


def train(model: nn.Module, train_data: data.DataLoader, val_data: data.DataLoader, config):
    device = config['setup_args']['device']
    model = model.to(device)
    optim = get_optimizer(model, config['exp_args']['optimizer'], config['exp_args']['lr'])
    sched = get_scheduler(optim, type=config['exp_args']['scheduler'])
    critereon = get_critereon()

    if config['setup_args']['resume'] is not None:
        raise NotImplementedError()

    init_epoch = 0
    for epoch in range(init_epoch, config['exp_args']['epoch']):
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


