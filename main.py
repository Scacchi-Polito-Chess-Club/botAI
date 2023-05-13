import yaml
from models.autoencoder import *
import games_from_dataset as gd


def main():
    with open("setup/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    # if you want to change some parameters, you can edit dictionary config (ex. config[par1][par1.1]=val)

    if config['setup_args']['looger'] is not None:
        raise NotImplementedError('logging not implemented yet')
    model = AutoEncoder(config)
    train_data, val_data, test_data = gd.get_dataloader(fname=config['data_loader']['data_path'],
                                                        num_workers=config['data_loader']['n_workers'],
                                                        batch_size=config['exp_args']['batch_size'],
                                                        board_transform=gd.board_to_array2)

    if config['exp_args']['type_exp'] == 'train':
        train(model, train_data, val_data, config)
        test(model)
    elif config['exp_args']['type_exp'] == 'test':
        ckpt = torch.load(config['setup_args']['resume'])
        model.load_state_dict(ckpt['model_state_dict'], strict=True)
        test(model)


if __name__ == '__main__':
    main()
