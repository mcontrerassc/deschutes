import pandas as pd
import pathlib as pl
from glob import glob
import numpy as np

stv_results = glob(f"stv_sim/stv_results/*")
plu_results = glob(f"stv_sim/plu_results/*")

results_df_orig = pd.DataFrame(
    data = {
        "winners" : [],
        "config" : []
    }
)

for results_file in stv_results:
    df = (
        pd.read_json(results_file, lines=True)
        .assign(config = pl.Path(results_file).stem)
    )
    results_df_orig = pd.concat([results_df_orig, df])

for results_file in plu_results:
    df = (
        pd.read_json(results_file, lines=True)
        .assign(config = pl.Path(results_file).stem)
    )
    results_df_orig = pd.concat([results_df_orig, df])

results_df = results_df_orig.reset_index()
results_df["partisan"] = results_df['config'].str.extract("(\\(.*?\\))", expand=False)
results_df["config"] = results_df['config'].str.replace("(\\(.*?\\)\\_)", "", regex = True)
results_df["slates"] = results_df['config'].str.extract("(\\(.*?\\))", expand=False)
results_df["config"] = results_df['config'].str.replace("(\\(.*?\\)\\_)", "", regex = True)
results_df["election_type"] = results_df['config'].str.extract("^(.*?)\\_", expand=False).astype("category")
results_df["config"] = results_df['config'].str.replace("^(.*?\\_)", "", regex = True)
results_df["generator"] = results_df['config'].str.extract("^(.*?)\\_voters", expand=False).astype("category")
results_df["config"] = results_df['config'].str.replace("^(.*?\\_)voters", "", regex = True)
results_df["voters"] = pd.to_numeric(results_df['config'].str.extract("(\\d+)", expand=False))
results_df["config"] = results_df['config'].str.replace("(\\d+)", "", regex = True, n = 1)
results_df["seats"] = pd.to_numeric(results_df['config'].str.extract("(\\d+)", expand=False))
results_df["config"] = results_df['config'].str.replace("(\\d+)", "", regex = True, n = 1)
results_df["samples"] = pd.to_numeric(results_df['config'].str.extract("(\\d+)", expand=False))
results_df["config"] = results_df['config'].str.replace("(\\d+)", "", regex = True, n = 1)
results_df["d_bloc_size"] = pd.to_numeric(results_df['partisan'].str.extract("([123456789]+)", expand=False)) / 100

d_slate_conditions = [
    results_df['slates'].str.contains("dumb\\_"),
    results_df['slates'].str.contains("naive\\_"),
    results_df['slates'].str.contains("smart\\_"),]
d_slate_choices = [10, 5, 3]
results_df['d_cands'] = np.select(d_slate_conditions, d_slate_choices, default=1)

r_slate_conditions = [
    results_df['slates'].str.contains("\\_dumb"),
    results_df['slates'].str.contains("\\_naive"),
    results_df['slates'].str.contains("\\_smart"),]
r_slate_choices = [10, 5, 3]
results_df['r_cands'] = np.select(r_slate_conditions, r_slate_choices, default=1)
results_df = results_df.drop(["index", "config", "partisan", "slates"], axis = 1)
results_df["ds_elected"] = results_df["winners"].str.join(" ").str.count("D")

results_df.groupby("election_type")[["ds_elected"]].agg("value_counts", dropna = False)

stv_results = (
    results_df
    .query('election_type == "stv"')
    .reset_index()
    .query("d_bloc_size in [0.45, 0.05, 0.55]")
    .query("d_cands == 5")
    .query("r_cands == 5")
    .query("samples == 500")
)
plu_results = results_df.query('election_type == "plurality"').reset_index().reset_index().query("samples == 2500")
plu_results["fives"] = plu_results["level_0"] // 5

plu_combined = (
    plu_results
    .groupby(["election_type", "generator", "voters", "samples", "d_bloc_size", "fives"])
    .agg(
        seats=("seats", "sum"), 
        ds_elected=("ds_elected", "sum")
    )
).reset_index().query("seats > 0").query("d_bloc_size in [0.45, 0.05, 0.55]")
plu_combined["samples"] = plu_combined["samples"] / 5

full_results = pd.concat([stv_results, plu_combined]).reset_index()
full_results = full_results.drop(["index", "level_0", "winners", "fives"], axis = 1)
full_results.loc[full_results['d_bloc_size'] < .1, 'd_bloc_size'] = full_results.loc[full_results['d_bloc_size'] < 0.1, 'd_bloc_size'] * 10
full_results["d_bloc_size"] = full_results["d_bloc_size"].astype("category")

from lets_plot import *
LetsPlot.setup_html()

plurality = full_results.query("election_type == 'plurality'")
stv = full_results.query("election_type == 'stv'")
partisan_plot = (
    ggplot(full_results, aes(x="ds_elected")) 
        + geom_bar()
        + facet_grid("d_bloc_size", "election_type")
        + labs(x = "Number of Democrats elected",
               y = "Simulated elections",
               title = "STV returns more consistent partisan representation than plurality elections",
               subtitle = "Partisan majorities don't become blowouts, \nand a split field always returns a split council",
               caption = "500 simulated elections representing Deschutes County, Oregon, in each sextant"
               )
)
ggsave(partisan_plot, "partisan_plot.svg")
