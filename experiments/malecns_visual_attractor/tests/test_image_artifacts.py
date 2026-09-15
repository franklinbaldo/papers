from pathlib import Path

import numpy as np

from image_artifacts import rasterize_receptors, write_gray_png


def test_write_gray_png_and_rasterize(tmp_path: Path):
    values = np.asarray([0.2, 0.8, 0.5], dtype=np.float32)
    x = np.asarray([-1.0, 0.0, 1.0], dtype=np.float32)
    y = np.asarray([-1.0, 0.0, 1.0], dtype=np.float32)
    resolved = np.asarray([True, True, False])
    image = rasterize_receptors(values, x, y, resolved, width=64, height=32, radius=1)
    assert image.shape == (32, 64)
    assert float(image.max()) == np.float32(0.8)
    path = tmp_path / "retina.png"
    write_gray_png(path, image, normalize=True)
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 50
