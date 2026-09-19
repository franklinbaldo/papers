from __future__ import annotations

import json

from sensor_slice_admission import AdmissionPolicy, assess_scalar_pair


POLICY = AdmissionPolicy(
    max_timestamp_quantum_s=1.0,
    min_unique_timestamps=3,
    min_paired_fraction=0.95,
    min_rows_for_benchmark=100,
)

# Public LEVIN-schema test fixture preserving seconds. Source:
# AreHumphrey/InsureML@94b204b2dd63e20dec0d9801c4676c59d03ef363
# src/data/tests/v2_no_dtc.csv (blob effa9c8135c53002cb20ea97ce551f38c250ecd5)
SECONDS_FIXTURE = [
    {"timeStamp": "2017-12-22 18:43:05", "gps_speed": 24.2612, "speed": 23.0},
    {"timeStamp": "2017-12-22 18:43:06", "gps_speed": 23.1500, "speed": 21.0},
    {"timeStamp": "2017-12-22 18:43:07", "gps_speed": 18.7052, "speed": 17.0},
]

# Ten-row compatibility probe from a public LEVIN derivative. Source:
# mukul-bhele/vehicletelematics@508333cf545f531e9a0dbdcf561f50114bd8ef16
# Dataset/Complete Dataset (After Analysis).csv
# blob 104c5cfb239875bd04fcc8031bdae72bfc2d755b. The derivative renders
# timestamps only to the minute, which is the property under test here.
MINUTE_DERIVATIVE_HEAD = [
    {"timeStamp": "07-12-2017 16:48", "gps_speed": 48.1520, "speed": 41.0},
    {"timeStamp": "07-12-2017 16:48", "gps_speed": 44.0776, "speed": 41.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 42.7812, "speed": 42.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 42.9664, "speed": 42.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 43.1516, "speed": 43.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 43.1516, "speed": 43.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 44.2628, "speed": 44.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 44.6332, "speed": 46.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 47.2260, "speed": 46.0},
    {"timeStamp": "07-12-2017 16:49", "gps_speed": 47.7816, "speed": 45.0},
]


def main() -> None:
    probes = {
        "seconds_fixture": assess_scalar_pair(
            SECONDS_FIXTURE,
            timestamp_key="timeStamp",
            left_key="gps_speed",
            right_key="speed",
            timestamp_format="%Y-%m-%d %H:%M:%S",
            policy=POLICY,
        ).to_dict(),
        "minute_derivative_head": assess_scalar_pair(
            MINUTE_DERIVATIVE_HEAD,
            timestamp_key="timeStamp",
            left_key="gps_speed",
            right_key="speed",
            timestamp_format="%d-%m-%Y %H:%M",
            policy=POLICY,
        ).to_dict(),
    }
    print(json.dumps(probes, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
