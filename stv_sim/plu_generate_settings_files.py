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

for dr_pair in dr_pairs:
        output_settings = dict(
            bloc_voter_prop={"D": dr_pair[0], "R": dr_pair[1]},
            cohesion_parameters={
                "D": {"D": 0.9, "R": 0.1},
                "R": {"D": 0.1, "R": 0.9},
            },
            alphas={"D": {"D": 1, "R": 1}, "R": {"D": 1, "R": 1}},
            slate_to_candidates={"D": ["D1"], 
                                 "R": ["R1"]},
        )

        output_dir = Path("stv_sim/plu_run_settings")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = Path(
            f"stv_sim/plu_run_settings/dr_({dr_pair[0]}_{dr_pair[1]})".replace(
                ".", "p"
            )
            + ".json"
        )

        with open(output_path, "w") as f:
            json.dump(output_settings, f, indent=4)
