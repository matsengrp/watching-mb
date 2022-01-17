#!/usr/bin/env python

import pickle
import click


def read_cdf(path_read, ci):
    pp_dict = {}
    tree_ci_list = []
    with open(path_read) as file:
        for line in file.readlines():
            (raw_pp, raw_cdf, _, nwk) = line.split()
            pp = float(raw_pp)
            pp_dict[nwk] = pp
            if float(raw_cdf) < ci:
                tree_ci_list.append(nwk)
    return (pp_dict, tree_ci_list)


@click.command()
@click.argument("read_path")
@click.argument("write_path")
def cli(read_path, write_path):
    """
    Take a list of trees in the CDF format and save a tuple consisting of:

    * a dictionary mapping all of the trees to their posterior probabilities
    * the list of trees in the 95% credible interval.
    """
    with open(write_path, "wb") as file:
        pickle.dump(read_cdf(read_path, 0.95), file)


if __name__ == "__main__":
    cli()
