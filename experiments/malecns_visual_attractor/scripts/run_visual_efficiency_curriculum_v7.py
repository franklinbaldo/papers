from __future__ import annotations

import json
import sys
from pathlib import Path

import run_visual_efficiency_curriculum_v6 as v6


def main() -> None:
    """Continue the six-blob curriculum from a persisted transducer checkpoint.

    v7 intentionally keeps the v6 renderer and exact-energy policy unchanged.
    The experimental change is the training schedule supplied by the bridge:
    more generations and a lower final visual-energy budget.
    """
    v6.main()

    try:
        output_dir = Path(sys.argv[sys.argv.index("--output-dir") + 1])
    except (ValueError, IndexError) as exc:
        raise RuntimeError("v7 requires explicit --output-dir") from exc

    summary_path = output_dir / "visual-efficiency-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["experiment"] = "malecns-visual-efficiency-curriculum-v7-resumed-low-light"
    summary["scientific_status"] = (
        "engineering calibration; resumed six-blob transducer with exact-energy matching and lower-light curriculum"
    )
    summary["training_policy"] = {
        "renderer": "six-blob body-latent field from v6",
        "resume_required_for_primary_run": True,
        "goal": "continue optimizing structured visual advantage while reducing delivered light",
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "event": "visual_efficiency_v7_complete",
                "learning_mode": summary.get("learning_state", {}).get("mode"),
                "budgets": summary.get("parameters", {}).get("budgets"),
                "max_energy_mismatch": summary.get("max_energy_mismatch_all_stages"),
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
