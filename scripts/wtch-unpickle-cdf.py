#!/usr/bin/env python

import pickle
import os
import click


@click.command()
@click.argument("read_path")
@click.argument("write_path")
def cli(read_path, write_path):
    """
    Take a pickle file containing a tuple, where the second entry is a list of trees,
    and write the trees to file as plain text.
    """
    tree_list = pickle.load(open(read_path, "rb"))[1]
    with open(write_path, "wt") as out_file:
        for tree in tree_list:
            out_file.write(tree + "\n")


if __name__ == "__main__":
    cli()
