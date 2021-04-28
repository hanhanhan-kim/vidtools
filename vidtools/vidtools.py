from pathlib import Path
from pprint import pprint

import click
import yaml

pass_config = click.make_pass_decorator(dict)

# TODO: add a DEFAULT_CONFIG ?

def load_config(fname):
    if fname == None:
        fname = "config.yaml"

    if Path(fname).exists():
        with open(fname) as f:
            config = yaml.safe_load(f) 
    else:
        config = dict()
        exit("You did not pass in a .yaml file! Please pass in a .yaml file.")

    return config

@click.group()
@click.option('--config', type=click.Path(exists=True, dir_okay=False),
              help='The config file to use instead of the default `config.yaml`.')
@click.pass_context
def cli(ctx, config):
    ctx.obj = load_config(config)

@cli.command()
@pass_config
def print_config(config):
    pprint(config)

@cli.command()
@pass_config
def h264_to_mp4(config):
    click.echo("Converting ...")
    from vidtools import h264_to_mp4
    h264_to_mp4.main(config)

@cli.command()
@pass_config
def undistort(config):
    click.echo("Undistorting ...")
    from vidtools import undistort
    undistort.main(config)

@cli.command()
@pass_config
def get_pxls_to_real(config):
    click.echo("Calculating conversion factor ...")
    from vidtools import pxls_to_real
    pxls_to_real.main(config)

# TODO: Turn bias_mjpg_to_avi and fmf_to_vid into cli commands 


if __name__ == "__main__":
    cli()