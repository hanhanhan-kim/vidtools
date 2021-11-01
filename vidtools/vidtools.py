from pathlib import Path
from pprint import pprint
from os.path import dirname, realpath, join

import click
import yaml

from vidtools.common import parse_readme_for_docstrings, docstring_parameter


readme_dir = dirname(dirname(realpath(__file__)))
docstrings = parse_readme_for_docstrings(join(readme_dir, "README.md"))
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
@docstring_parameter(docstrings["print-config"])
def print_config(config):
    """
    {0}
    """
    print("")
    pprint(config)
    print("")

@cli.command()
@pass_config
@docstring_parameter(docstrings["vid-to-imgs"])
def vid_to_imgs(config):
    """
    {0}
    """
    from vidtools import vid_to_imgs
    click.echo("\nConverting ...")
    vid_to_imgs.main(config)

@cli.command()
@pass_config
@docstring_parameter(docstrings["h264-to-mp4"])
def h264_to_mp4(config):
    """
    {0}
    """
    from vidtools import h264_to_mp4
    click.echo("\nConverting ...")
    h264_to_mp4.main(config)

@cli.command()
@pass_config
@docstring_parameter(docstrings["undistort"])
def undistort(config):
    """
    {0}
    """
    from vidtools import undistort
    click.echo("\nUndistorting ...")
    undistort.main(config)

@cli.command()
@pass_config
@docstring_parameter(docstrings["pxls-to-real"])
def pxls_to_real(config):
    """
    {0}
    """
    from vidtools import pxls_to_real
    click.echo("\nCalculating conversion factor ...")
    pxls_to_real.main(config)

@cli.command()
@pass_config
@docstring_parameter(docstrings["make-timelapse"])
def make_timelapse(config):
    """
    {0}
    """
    from vidtools import make_timelapse
    click.echo("\nGenerating timelapse ...")
    make_timelapse.main(config)

# TODO: Rename this command to something like ... circle-mask-and-crop
@cli.command()
@pass_config
@docstring_parameter(docstrings["find-circle"])
def find_circle(config):
    """
    {0}
    """
    from vidtools import find_circle
    click.echo("\nFinding circles ...")
    find_circle.main(config)

@cli.command()
@pass_config
@docstring_parameter(docstrings["track-blobs"])
def track_blobs(config):
    """
    {0}
    """
    from vidtools import track_blobs
    click.echo("\nLooking for blobs ...")
    track_blobs.main(config)

# TODO: Turn bias_mjpg_to_avi and fmf_to_vid into cli commands 


if __name__ == "__main__":
    cli()