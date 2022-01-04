import pickle

import bito
import click


def build_sdag_trees(read_collection_path, write_sdag_path):
    mmap_path = "_ignore/mmap.dat"
    fasta_path = "../data/ds7.fasta"
    inst = bito.gp_instance(mmap_path)
    inst.read_fasta_file(fasta_path)
    inst.read_newick_file(read_collection_path)
    inst.make_engine()
    inst.print_status()
    inst.export_all_generated_trees(write_sdag_path)


def count_pp(pp_dict, tree_ci_list):
    sum_pp = 0.0
    count_in_ci = 0
    for tree in tree_ci_list:
        sum_pp += pp_dict[tree]
        if tree in tree_ci_list:
            count_in_ci += 1
    return sum_pp, count_in_ci


@click.command()
@click.argument("sample_trees_path")
@click.argument("write_sdag_path")
@click.argument("pickle_path")
def cli(sample_trees_path, write_sdag_path, pickle_path):
    """Takes a collection of trees (S_k sampled from MCMC) and the pickle,
    builds an sDAG, writes the corresponding collection of trees to a temp file
    returns (1) the sum of the corresponding PPs for that collection of trees,
    and (2) the number of trees in the 95% credible interval

    Example usage:
    python generate-sdag-trees.py _ignore/rerooted-topologies.noburnin.10000.nwk\
        _ignore/sdag-trees.10000.nwk _ignore/golden.pickle
    """
    pp_dict, tree_ci_list = pickle.load(open(pickle_path, "rb"))
    build_sdag_trees(sample_trees_path, write_sdag_path)
    sum_pp, count_in_ci = count_pp(pp_dict, tree_ci_list)
    click.echo(f"{sum_pp} {count_in_ci}")


if __name__ == "__main__":
    cli()
