def test_stationary_screen_runner_imports():
    import runpy
    from pathlib import Path

    path = Path(__file__).parents[1] / "scripts" / "run_stationary_screen_reward_loop.py"
    assert path.exists()
