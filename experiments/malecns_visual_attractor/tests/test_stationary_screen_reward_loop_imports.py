from screen_reward_loop import LATENT_DIM, SCREEN_DIM


def test_screen_reward_dimensions_are_frozen():
    assert LATENT_DIM == 6
    assert SCREEN_DIM == 6
