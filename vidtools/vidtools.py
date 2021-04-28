from pathlib import Path

import click
import yaml

pass_config = click.make_pass_decorator(dict)

# DEFAULT_CONFIG = {
#     "undistort": {
#         "frame": 30
#         "m_corners": 6
#         "n_corners": 7
#     }
# }

def load_config(fname):
    if fname == None:
        fname = "config.yaml"

    if Path(fname).exists():
        with open(fname) as f:
            config = yaml.safe_load(f) 
    else:
        config = dict()

    return config

@click.group()
@click.option('--config', type=click.Path(exists=True, dir_okay=False),
              help='The config file to use instead of the default "config.yaml" .')
@click.pass_context
def cli(ctx, config):
    ctx.obj = load_config(config)

@cli.command()
@pass_config
def print_config(config):
    click.echo(config)


if __name__ == "__main__":
    cli()