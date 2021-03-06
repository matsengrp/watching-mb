#!/usr/bin/env python
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import pathlib
from collections import namedtuple
import click


GoldenData = namedtuple("GoldenData", "pp_dict credible_set")


def golden_data_of_path(golden_pickle_path):
    pp_dict, tree_ci_list = pickle.load(open(golden_pickle_path, "rb"))
    return GoldenData(pp_dict, set(tree_ci_list))


def dict_of_json(json_path):
    with open(json_path, "r") as json_file:
        return json.load(json_file)


def mcmc_df_of_topology_sequence(topology_sequence_path, golden):
    pathlib.Path("topologies-seen").mkdir(exist_ok=True)
    df = pd.read_csv(
        topology_sequence_path, delimiter="\t", names=["dwell_count", "topology"]
    )
    # The set of topologies seen so far.
    seen = set()
    # A list that tracks each topology observed in the sequence and marks if it was seen
    # for the first time.
    first_time = []

    for topology in df["topology"]:
        if topology in seen:
            first_time.append(False)
        else:
            first_time.append(True)
            seen.add(topology)
    df["first_time"] = first_time
    df["support_size"] = df["first_time"].cumsum()
    df["mcmc_iters"] = df["dwell_count"].cumsum()
    df["pp"] = df["topology"].apply(lambda t: golden.pp_dict.get(t, 0.0))
    df["total_pp"] = (df["pp"] * df["first_time"]).cumsum()
    df["in_credible_set"] = df["topology"].apply(golden.credible_set.__contains__)
    df["credible_set_found"] = (df["in_credible_set"] & df["first_time"]).cumsum()
    df["credible_set_frac"] = df["credible_set_found"] / len(golden.credible_set)
    return df


def indexer_reps_of_path(path, sort=True):
    representations = []
    with open(path) as the_file:
        for line in the_file:
            # After the last comma is either an empty entry or the log-likelihood.
            rep = [int(j) for j in line.split(",")[:-1]]
            if sort:
                rep.sort()
            representations.append(rep)
    return representations


def nni_results_df_of(nni_rep_path, credible_rep_path, pp_rep_path, pp_values_path):
    nni_reps = indexer_reps_of_path(nni_rep_path, sort=False)
    cred_set_reps = indexer_reps_of_path(credible_rep_path, sort=True)
    pp_set_reps = indexer_reps_of_path(pp_rep_path, sort=True)
    with open(pp_values_path) as the_file:
        pp_set_values = [float(line.strip()) for line in the_file]

    sdag_increased = []
    seen_indices = set()
    for rep in nni_reps:
        rep_set = set(rep)
        has_new_indices = not rep_set.issubset(seen_indices)
        sdag_increased.append(has_new_indices)
        if has_new_indices:
            seen_indices.update(rep_set)

    nni_reps = [",".join(map(str, rep)) for rep in nni_reps]
    cred_set_reps = [",".join(map(str, rep)) for rep in cred_set_reps]
    pp_set_reps = [",".join(map(str, rep)) for rep in pp_set_reps]
    rep_to_pp = dict(zip(pp_set_reps, pp_set_values))

    nni_results_df = pd.DataFrame(nni_reps, columns=["pcsp_rep"])
    nni_results_df["support_size"] = range(1, len(nni_reps) + 1)
    nni_results_df["is_cred"] = [rep in cred_set_reps for rep in nni_reps]
    nni_results_df["pp"] = [rep_to_pp.get(rep, 0.0) for rep in nni_reps]
    nni_results_df["total_pp"] = nni_results_df["pp"].cumsum()
    nni_results_df["cred_total"] = nni_results_df["is_cred"].cumsum()
    nni_results_df["cred_frac"] = nni_results_df["cred_total"] / len(cred_set_reps)
    nni_results_df["bigger_sdag"] = sdag_increased
    nni_results_df["comps_current"] = nni_results_df["bigger_sdag"] * 12
    nni_results_df["comps_current"].iloc[0] = 48
    nni_results_df["comps_total"] = nni_results_df["comps_current"].cumsum()
    nni_results_df["sdag_iter"] = nni_results_df["bigger_sdag"].cumsum()

    return nni_results_df


@click.command()
@click.argument("nni_rep_path")
@click.argument("cred_rep_path")
@click.argument("pp_rep_path")
@click.argument("pp_values_path")
@click.argument("golden_pickle_path")
@click.argument("topology_sequence_path")
def run(
    nni_rep_path,
    cred_rep_path,
    pp_rep_path,
    pp_values_path,
    golden_pickle_path,
    topology_sequence_path,
):
    golden = golden_data_of_path(golden_pickle_path)
    mcmc_df = mcmc_df_of_topology_sequence(topology_sequence_path, golden)
    mcmc_df.to_csv("mcmc.csv")
    last_mcmc_pp_idx = mcmc_df[mcmc_df["first_time"]]["total_pp"].idxmax()
    last_mcmc_cred_idx = mcmc_df[mcmc_df["first_time"]]["credible_set_found"].idxmax()
    mcmc_pp_df = mcmc_df.loc[: 1 + last_mcmc_pp_idx]
    mcmc_cred_df = mcmc_df.loc[: 1 + last_mcmc_cred_idx]

    nni_df = nni_results_df_of(nni_rep_path, cred_rep_path, pp_rep_path, pp_values_path)
    nni_df.to_csv("nni.csv")
    last_nni_sdag_idx = nni_df["sdag_iter"].idxmax()
    nni_sdag_df = nni_df.loc[: 1 + last_nni_sdag_idx]
    nni_sdag_df = nni_sdag_df[nni_sdag_df["bigger_sdag"]]

    last_nni_pp_idx = nni_sdag_df["total_pp"].idxmax()
    nni_pp_df = nni_sdag_df.loc[: 1 + last_nni_pp_idx]
    last_nni_cred_idx = nni_sdag_df["cred_total"].idxmax()
    nni_cred_df = nni_sdag_df.loc[: 1 + last_nni_cred_idx]

    mcmc_last_pp = mcmc_pp_df[["support_size", "total_pp", "mcmc_iters"]].iloc[-1]
    mcmc_last_cred = mcmc_cred_df[
        ["support_size", "credible_set_frac", "mcmc_iters"]
    ].iloc[-1]
    nni_last_pp = nni_pp_df[["sdag_iter", "total_pp", "support_size"]].iloc[-1]
    nni_last_cred = nni_cred_df[["sdag_iter", "cred_frac", "support_size"]].iloc[-1]

    fig, ax = plt.subplots()

    # Next we make a plot for each key with the specificed x_label, y_label, and save
    # to the specified out_path. Each plot consists of some number of lines, each line
    # using a dataset with an x_attribute, y_attribute, and line_label, and optionally
    # the last value of a specified attribute of the dataset.
    keys = ["mcmc_acc", "nni_acc", "nni_vs_mcmc_cred", "nni_vs_mcmc_pp", "comp_cred"]
    x_label = {
        "mcmc_acc": "mcmc iterations",
        "nni_acc": "sdag iteration",
        "nni_vs_mcmc_cred": "sdag iteration -- mcmc support",
        "nni_vs_mcmc_pp": "sdag iteration -- mcmc support",
        "comp_cred": "approximate likelihood calculations",
    }
    y_label = {
        "mcmc_acc": None,
        "nni_acc": None,
        "nni_vs_mcmc_cred": "ratio of credible set",
        "nni_vs_mcmc_pp": "cumulative posterior probability",
        "comp_cred": "ratio of credible set",
    }
    x_attr = {
        "mcmc_acc": ("mcmc_iters", "mcmc_iters"),
        "nni_acc": ("sdag_iter", "sdag_iter"),
        "nni_vs_mcmc_cred": ("sdag_iter", "support_size"),
        "nni_vs_mcmc_pp": ("sdag_iter", "support_size"),
        "comp_cred": ("comps_total", "mcmc_iters"),
    }
    y_attr = {
        "mcmc_acc": ("total_pp", "credible_set_frac"),
        "nni_acc": ("total_pp", "cred_frac"),
        "nni_vs_mcmc_cred": ("cred_frac", "credible_set_frac"),
        "nni_vs_mcmc_pp": ("total_pp", "total_pp"),
        "comp_cred": ("cred_frac", "credible_set_frac"),
    }
    data_set = {
        "mcmc_acc": (mcmc_pp_df, mcmc_pp_df),
        "nni_acc": (nni_pp_df, nni_pp_df),
        "nni_vs_mcmc_cred": (nni_cred_df, mcmc_cred_df),
        "nni_vs_mcmc_pp": (nni_pp_df, mcmc_pp_df),
        "comp_cred": (nni_cred_df, mcmc_cred_df),
    }
    line_label = {
        "mcmc_acc": ("total pp", "fraction of credible set"),
        "nni_acc": ("total pp", "fraction of credible set"),
        "nni_vs_mcmc_cred": ("nni-walk", "mcmc"),
        "nni_vs_mcmc_pp": ("nni-walk", "mcmc"),
        "comp_cred": ("nni-walk", "mcmc"),
    }
    extra_plot = {
        "mcmc_acc": (None, None),
        "nni_acc": (None, None),
        "nni_vs_mcmc_cred": (
            ("support_size", "sampled topologies", 0.75, 1.01),
            ("mcmc_iters", "\nmcmc\niterations", 1.01, 0.9),
        ),
        "nni_vs_mcmc_pp": (
            ("support_size", "sampled topologies", 0.8, 1.01),
            ("mcmc_iters", "mcmc iterations", 0.9, 0.95),
        ),
        "comp_cred": (None, None),
    }
    out_path = {
        "mcmc_acc": "mcmc_accumulation.pdf",
        "nni_acc": "nni_accumulation.pdf",
        "nni_vs_mcmc_cred": "sdag_iter_vs_mcmc_credible.pdf",
        "nni_vs_mcmc_pp": "sdag_iter_vs_mcmc_total_pp.pdf",
        "comp_cred": "computations_for_credible.pdf",
    }

    for key in keys:
        ax.set_xlabel(x_label[key], fontsize="x-large")
        if not y_label[key] is None:
            ax.set_ylabel(y_label[key], fontsize="x-large")
        stuff_to_plot = zip(
            x_attr[key], y_attr[key], data_set[key], line_label[key], extra_plot[key]
        )
        for the_x, the_y, the_data, the_line_label, the_extra in stuff_to_plot:
            ax.plot(the_x, the_y, data=the_data, label=the_line_label)
            if not the_extra is None:
                x, y, z = the_data[[the_x, the_y, the_extra[0]]].iloc[-1]
                plot_text = the_extra[1]
                print(f"{z} {plot_text} at ({x}, {y})")
                x *= the_extra[2]
                y *= the_extra[3]
                ax.text(x, y, f"{int(z)} {plot_text}", fontsize="x-small")
                ax.set_xlim(right=1.1 * ax.get_xlim()[1])
        ax.legend(fontsize="medium")
        ax.figure.savefig(out_path[key])
        ax.clear()


if __name__ == "__main__":
    run()
