import pickle
import bito
import pandas as pd
import tempfile
import os
import subprocess
import multiprocessing
import pathlib
​
​
def topology_set_of_path(topologies_path):
    with open(topologies_path) as topologies_file:
        return {t.strip() for t in topologies_file}
​
​
def topology_set_to_path(topology_set, topologies_path):
    with open(topologies_path, "w") as topologies_file:
        for topology in topology_set:
            topologies_file.write(topology + "\n")
​
​
def mcmc_df_of_topology_sequence(topology_sequence_path, pp_dict, credible_set):
    pathlib.Path("topologies-seen").mkdir(exist_ok=True)
    df = pd.read_csv(
        topology_sequence_path, delimiter="\t", names=["dwell_count", "topology"]
    )
    # The set of topologies seen so far.
    seen = set()
    # A list that tracks each topology observed in the sequence and marks if it was seen
    # for the first time.
    first_time = []
​
    def seen_to_file():
        topology_set_to_path(seen, f"topologies-seen/topologies-seen.{len(seen)}.nwk")
​
    for topology in df["topology"]:
        if topology in seen:
            first_time.append(False)
        else:
            first_time.append(True)
            seen.add(topology)
            seen_to_file()
    df["first_time"] = first_time
    df["support_size"] = df["first_time"].cumsum()
    df["mcmc_iters"] = df["dwell_count"].cumsum()
    df["pp"] = df["topology"].apply(lambda t: pp_dict.get(t, 0.0))
    df["total_pp"] = (df["pp"] * df["first_time"]).cumsum()
    df["in_credible_set"] = df["topology"].apply(credible_set.__contains__)
    df["credible_set_found"] = (df["in_credible_set"] & df["first_time"]).cumsum()
    df["credible_set_frac"] = df["credible_set_found"] / len(credible_set)
    df.set_index("mcmc_iters")
    return df
​
​
pickle_path = "golden.pkl"
pp_dict, credible_set_list = pickle.load(open(pickle_path, "rb"))
credible_set = set(credible_set_list)
​
df = mcmc_df_of_topology_sequence(
    "rerooted-topology-sequence.tab", pp_dict, credible_set
)
​
​
ax = df[["total_pp", "credible_set_frac"]].plot(ylim=[0, 1])
ax.figure.savefig("accumulation.pdf")
df.to_csv("accumulation.csv")
​
​
def build_sdag_trees(tmpdir, read_collection_path, write_sdag_trees_path):
    fasta_path = "ds.fasta"
    inst = bito.gp_instance(os.path.join(tmpdir, "mmap.dat"))
    inst.read_fasta_file(fasta_path)
    inst.read_newick_file(read_collection_path)
    inst.make_engine()
    inst.print_status()
    inst.export_all_generated_trees(write_sdag_trees_path)
    return inst.dag_summary_statistics()
​
​
def build_sdag_topologies_set_and_stats(topologies_seen_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        sdag_trees_path = os.path.join(tmpdir, "generated-trees.nwk")
        sdag_topologies_path = os.path.join(tmpdir, "sdag-topologies.nwk")
        sdag_summary_stats = build_sdag_trees(
            tmpdir, topologies_seen_path, sdag_trees_path
        )
        # TODO NOTE we have 7 here
        subprocess.check_call(
            f"nw_topology {sdag_trees_path} | nw_reroot - 7 | nw_order - "
            f"> {sdag_topologies_path}",
            shell=True,
        )
        return topology_set_of_path(sdag_topologies_path), sdag_summary_stats
​
​
def sdag_results_of_topology_count(topology_count):
    topologies_seen_path = f"topologies-seen/topologies-seen.{topology_count}.nwk"
    sdag_topologies_set, sdag_summary_stats = build_sdag_topologies_set_and_stats(
        topologies_seen_path
    )
    return [
        sdag_summary_stats["node_count"],
        sdag_summary_stats["edge_count"],
        len(credible_set.intersection(sdag_topologies_set)),
        len(sdag_topologies_set),
        sum(pp_dict.get(t, 0.0) for t in sdag_topologies_set),
    ]
​
​
total_seen_count = (
    int(subprocess.check_output("ls topologies-seen | wc -l", shell=True)) + 1
)
​
​
def sdag_results_df_of(max_topology_count):
    with multiprocessing.Pool() as pool:
        return pd.DataFrame(
            pool.map(sdag_results_of_topology_count, range(1, max_topology_count + 1)),
            columns=[
                "sdag_node_count",
                "sdag_edge_count",
                "sdag_topos_in_credible",
                "sdag_topos_total",
                "sdag_topos_total_pp",
            ],
        )
​
​
sdag_results_df = sdag_results_df_of(10)
sdag_results_df.to_csv("sdag-results.csv")
​
​
sdag_results_df.reset_index(inplace=True)
sdag_results_df["index"] += 1
sdag_results_df.rename(columns={"index": "support_size"}, inplace=True)
sdag_results_df["sdag_credible_set_frac"] = sdag_results_df[
    "sdag_topos_in_credible"
] / len(credible_set)
sdag_results_df.tail()
​
final_df = df.merge(sdag_results_df)
final_df.to_csv(
    "final-df.csv",
    columns=[
        "support_size",
        "mcmc_iters",
        "total_pp",
        "in_credible_set",
        "credible_set_found",
        "credible_set_frac",
        "sdag_edge_count",
        "sdag_node_count",
        "sdag_topos_in_credible",
        "sdag_topos_total",
        "sdag_topos_total_pp",
        "sdag_credible_set_frac",
    ],
)
​
​
ax = final_df[["total_pp", "sdag_total_pp"]].plot(ylim=[0, 1])
ax.figure.savefig("pp-accumulation.pdf")
​
ax = final_df[["credible_set_frac", "sdag_credible_set_frac"]].plot(ylim=[0, 1])
ax.figure.savefig("credible-accumulation.pdf")