from datetime import datetime as time

import torch
import yaml

import games_from_dataset as gd
from actionspace import encode_move
from experiment_launcher import train, test
from logs.local_logging import make_logger
from models.autoencoder import *
import wandb


def main():
    with open("setup/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    # if you want to change some parameters, you can edit dictionary config (ex. config[par1][par1.1]=val)
    logger = make_logger(config['setup_args']['logger'])
    # logger.info(f"{str(logger)} is available")
    model = AutoEncoder(config)
    train_data, val_data, test_data = gd.get_dataloader(fname=config['data_loader']['data_path'],
                                                        batch_size=config['exp_args']['batch_size'],
                                                        num_workers=config['data_loader']['n_workers'],
                                                        board_transform='matrix', move_transform=encode_move)

    wandb_name = config['setup_args']['wandb_name'] \
        if config['setup_args']['wandb_name'] is not None else f'run_{time.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    if config['setup_args']['wandblog'] is True:
        wandb.init(
            project="scacchi-polito-bot-ai",
            config=config,
            name=wandb_name
        )

    if config['exp_args']['type_exp'] == 'train':
        train(model, train_data, val_data, config, logger)
        test(model, test_data, config, logger)
    elif config['exp_args']['type_exp'] == 'test':
        ckpt = torch.load(config['setup_args']['resume'])
        model.load_state_dict(ckpt['model_state_dict'], strict=True)
        test(model, logger)


if __name__ == '__main__':
    main()
