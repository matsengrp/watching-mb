"""Command line interface."""

import json
import sys
import click
import wmb.templating as templating


# Entry point
def safe_cli():
    """Top-level CLI for subcommands."""
    try:
        cli()
    except Exception as exception:
        print("Exception raised when running the command:\n")
        print(" ".join(sys.argv) + "\n")
        raise exception


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
def cli():
    """Top-level CLI for subcommands."""
    pass  # pylint: disable=unnecessary-pass


@cli.command()
@click.argument("template_name", required=True)
@click.argument("settings_json", required=True, type=click.Path(exists=True))
@click.argument("dest_path", required=True, type=click.Path(exists=False))
@click.option(
    "--template-dir", help="Directory containing templates.", default="templates"
)
@click.option("--make-paths-absolute", is_flag=True, help="Make paths absolute.")
@click.option("--mb", is_flag=True, help="Perform MB-specific parameter expansion.")
def template(
    template_name, settings_json, dest_path, template_dir, make_paths_absolute, mb
):
    """Generate a file using a template found in the current directory with the
    settings."""
    with open(settings_json, "r") as file:
        settings_dict = json.load(file)

    if mb:
        templating.expand_mb_settings(settings_dict)

    if make_paths_absolute:
        templating.make_paths_absolute(settings_dict)

    templating.template_file(template_name, template_dir, settings_dict, dest_path)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
