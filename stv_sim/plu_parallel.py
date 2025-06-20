from itertools import product
import joblib
from joblib_progress import joblib_progress
import json
from glob import glob
import pathlib as pl
from votekit_cli_many import run_election
import warnings

warnings.filterwarnings("ignore")


if __name__ == "__main__":
    n_simultaneous_jobs = 10
    settings_files = glob("stv_sim/plu_run_settings/*.json")

    output_dir = pl.Path("stv_sim/plu_results").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    ballot_generators = [
        "slate_pl",
    ]
    num_voters = [1000]

    election_types = [
        "plurality"
    ]
    num_seats = [1]
    num_iterations = [2500]

    full_settings_list = []
    for settings in product(
        ballot_generators,
        num_voters,
        num_seats,
        election_types,
        num_iterations,
        settings_files,
    ):
        (
            ballot_generator,
            num_voters,
            num_seats,
            election_type,
            num_iterations,
            settings_file,
        ) = settings
        output_file = (
            output_dir
            / f"{election_type}_{ballot_generator}_voters_{num_voters}_seats_{num_seats}_samples_{num_iterations}_{pl.Path(settings_file).stem}.jsonl"
        )

        with open(settings_file, "r") as f:
            ballot_generator_kwargs = json.load(f)
        if ballot_generator_kwargs is None:
            ballot_generator_kwargs = {}

        full_settings_list.append(
            dict(
                ballot_generator=ballot_generator,
                num_voters=num_voters,
                num_seats=num_seats,
                election_type=election_type,
                num_iterations=num_iterations,
                ballot_generator_kwargs=ballot_generator_kwargs,
                output_file=output_file,
            )
        )

    with joblib_progress(
        total=len(full_settings_list), description="Running elections"
    ):
        results = joblib.Parallel(n_jobs=n_simultaneous_jobs)(
            joblib.delayed(run_election)(**settings_dict)
            for settings_dict in full_settings_list
        )
