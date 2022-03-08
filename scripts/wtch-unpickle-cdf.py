#!/usr/bin/env python

import pickle
import os
import click


@click.command()
@click.argument("read_path")
@click.argument("tree_write_path")
@click.argument("pp_tree_write_path")
@click.argument("pp_value_write_path")
def cli(read_path, tree_write_path, pp_tree_write_path, pp_value_write_path):
    """ ...update this comment...
    Take a pickle file containing a tuple, where the second entry is a list of trees,
    and write the trees to file as plain text.
    """
    
    pp_dict, tree_list = pickle.load(open(read_path, "rb"))
    with open(tree_write_path, "wt") as out_file:
        for tree in tree_list:
            out_file.write(tree + "\n")
    with open(pp_tree_write_path, "wt") as out_file:
        for tree in pp_dict.keys():
            out_file.write(tree + "\n")
    with open(pp_value_write_path, "wt") as out_file:
        for tree in pp_dict.keys():
            out_file.write(str(pp_dict[tree]) + "\n")



if __name__ == "__main__":
    cli()
