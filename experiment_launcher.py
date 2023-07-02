import torch.optim
import torch.utils.data as data
import tqdm
from utils.utils_model import *
import wandb


@torch.no_grad()
def test(model:nn.Module, test_data: data.DataLoader, config, logger):
    device = config['setup_args']['device']
    loss_func = get_loss_func(config['exp_args']['loss'])
    corrects = 0
    totals = 0
    tot_loss = 0.0
    for (b1, b2), move_gt in test_data:
        b1, b2, move_gt = b1.to(device).float(), b2.to(device).float(), move_gt.to(device).float()
        move = model(b1, b2)
        predicted_move = torch.argmax(move, axis=-1)
        gt = torch.argmax(move_gt, axis=-1)
        corrects += torch.sum(predicted_move == gt)
        totals += predicted_move.shape[0]
        tot_loss += loss_func(move, move_gt).item()
    accuracy = (corrects/totals).detach().cpu().numpy()
    avg_loss = tot_loss / len(test_data)
    if logger is not None:
        logger.info(f"Eval accuracy {accuracy}, Eval avg loss {avg_loss}")
        wandb.log({"Eval accuracy": accuracy, "Eval avg loss": avg_loss})
    return accuracy, avg_loss


def train(model: nn.Module, train_data: data.DataLoader, val_data: data.DataLoader, config, logger):
    device = config['setup_args']['device']
    model = model.to(device)
    optim = get_optimizer(model, config['exp_args']['optimizer'].lower(), config['exp_args']['lr'])
    sched = get_scheduler(optim, type=config['exp_args']['scheduler'])
    loss_func = get_loss_func(config['exp_args']['loss'])

    if config['setup_args']['resume']:
        raise NotImplementedError()
    if logger is not None:
        logger.info('Start Training')
    init_epoch = 0
    for epoch in range(init_epoch, config['exp_args']['epoch']):
        tot_loss = 0.0
        corrects = 0
        totals = 0
        loss = torch.tensor(0.0)
        data_iterator = tqdm.tqdm(train_data)
        for (b1, b2), action_gt in data_iterator:
            data_iterator.set_description(f'Training epoch {epoch}, training loss {loss.item():5f}')
            b1, b2 = b1.to(device).float(), b2.to(device).float()
            action_gt = action_gt.to(device).float()
            optim.zero_grad()
            action = model(b1, b2)
            loss = loss_func(action, action_gt)
            loss.backward()
            optim.step()
            tot_loss += loss.item()
            predicted_move = torch.argmax(action, axis=-1)
            gt = torch.argmax(action_gt, axis=-1)
            corrects += torch.sum(predicted_move == gt)
            totals += predicted_move.shape[0]
        sched.step()
        if logger is not None:
            logger.info(f"Epoch {epoch}: avg loss  {tot_loss / len(train_data)}")
            wandb.log({"Epoch": epoch, "avg loss":  tot_loss / len(train_data)})
        if epoch % config['exp_args']['eval_step'] == 0:
            test(model, val_data, config, logger)

    return model


