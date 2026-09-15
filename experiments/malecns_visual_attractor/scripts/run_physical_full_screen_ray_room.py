from __future__ import annotations

import run_physical_full_screen_compound_eye as compound
from compound_eye_environment import front_of_tv_starts


def main() -> None:
    # Replace the old 360-degree target starts: every batch member is an
    # independent physical-room replicate in front of the same x=0 TV wall.
    compound.base.matched_offset_starts = front_of_tv_starts
    compound.main()


if __name__ == "__main__":
    main()
