from itertools import product
import json
from pathlib import Path


if __name__ == "__main__":
    dr_pairs = [
        (.45, .55),
        (.46, .54),
        (.47, .53),
        (.48, .52),
        (.49, .51),
        (.50, .50),
        (.51, .49),
        (.52, .48),
        (.53, .47),
        (.54, .46),
        (.55, .45)
    ]

slate_dict = {
    "naive_naive" : (5, 5),
    "dumb_naive" : (10, 5),
    "naive_dumb" : (5, 10),
    "smart_naive" : (3, 5),
    "naive_smart" : (5, 3),
    "smart_smart" : (3, 3)
}
slate_names = list(slate_dict.keys())

for dr_pair, slate_name in product(dr_pairs, slate_names):
        slate_tup = slate_dict[slate_name]
        output_settings = dict(
            bloc_voter_prop={"D": dr_pair[0], "R": dr_pair[1]},
            cohesion_parameters={
                "D": {"D": 0.9, "R": 0.1},
                "R": {"D": 0.1, "R": 0.9},
            },
            alphas={"D": {"D": 1, "R": 1}, "R": {"D": 1, "R": 1}},
            slate_to_candidates={"D": [f"D{i+1}" for i in range(0, slate_tup[0])], 
                                 "R": [f"R{i+1}" for i in range(0, slate_tup[1])]},
        )

        output_dir = Path("stv_sim/stv_run_settings")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = Path(
            f"stv_sim/stv_run_settings/dr_({dr_pair[0]}_{dr_pair[1]})_slate_({slate_name})".replace(
                ".", "p"
            )
            + ".json"
        )

        with open(output_path, "w") as f:
            json.dump(output_settings, f, indent=4)
