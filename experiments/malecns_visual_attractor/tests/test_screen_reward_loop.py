import numpy as np

from screen_reward_loop import (
    ScreenGeometry,
    initial_transducer,
    make_transducer_population,
    matched_direct_gaze_starts,
    select_winner,
    sensor_grid_ascii,
    top_receptors,
)


def geometry(n=10):
    return ScreenGeometry(
        bodies=np.arange(100, 100 + n, dtype=np.int64),
        x=np.linspace(-1, 1, n, dtype=np.float32),
        y=np.linspace(1, -1, n, dtype=np.float32),
        resolved=np.asarray([(i % 2) == 0 for i in range(n)], dtype=bool),
        eye=np.asarray([-1 if i < n // 2 else 1 for i in range(n)], dtype=np.int8),
    )


def test_direct_gaze_starts_face_origin():
    x, y, heading = matched_direct_gaze_starts(flies=8, radius=1.0, seed=3)
    bearing = np.arctan2(-y, -x)
    np.testing.assert_allclose(np.angle(np.exp(1j * (heading - bearing))), 0.0, atol=1e-12)


def test_population_keeps_center_as_candidate_zero():
    weight, bias = initial_transducer(seed=4)
    pop_w, pop_b = make_transducer_population(
        weight, bias, population=5, sigma=0.2, seed=5
    )
    np.testing.assert_array_equal(pop_w[0], weight)
    np.testing.assert_array_equal(pop_b[0], bias)
    assert not np.array_equal(pop_w[1], weight)


def test_sensor_grid_contains_one_cell_per_sensor():
    g = geometry(130)
    values = np.linspace(0, 1, 130, dtype=np.float32)
    rendered = sensor_grid_ascii(values, g, width=64)
    cells = sum(len(line) for line in rendered.splitlines())
    assert cells == 130


def test_top_receptors_and_winner_are_deterministic():
    g = geometry(5)
    values = np.asarray([0.1, 0.9, 0.2, 0.8, 0.3], dtype=np.float32)
    top = top_receptors(values, g, k=2)
    assert [row["body"] for row in top] == [101, 103]
    assert select_winner(np.asarray([1.0, 3.0, 2.0])) == 1
