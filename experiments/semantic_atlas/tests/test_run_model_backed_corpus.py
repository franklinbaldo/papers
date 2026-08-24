import hashlib
import importlib.util
import subprocess
from pathlib import Path

_SCRIPT = Path(__file__).parents[1] / "scripts" / "run_model_backed_a.py"
_SPEC = importlib.util.spec_from_file_location("run_model_backed_a", _SCRIPT)
run_model_backed_a = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_model_backed_a)


def _git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=str(cwd), text=True)


def _seed_nested_repo(tmp_path: Path) -> tuple[Path, Path, str]:
    """Repo with markdown files outside experiments/semantic_atlas."""
    root = tmp_path / "repo"
    package = root / "experiments" / "semantic_atlas"
    package.mkdir(parents=True)
    domains = root / "papers"
    domains.mkdir()
    for name in ("a.md", "b.md"):
        (domains / name).write_text(f"# {name}\n", encoding="utf-8")
    (package / "README.md").write_text("# readme\n", encoding="utf-8")
    (package / "notes.txt").write_text("not markdown\n", encoding="utf-8")
    _git("init", "-q", cwd=root)
    _git("config", "user.email", "test@example.com", cwd=root)
    _git("config", "user.name", "Test Runner", cwd=root)
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", "seed corpus", cwd=root)
    sha = _git("rev-parse", "HEAD", cwd=root).strip()
    return package, root, sha


def test_git_paths_enumerates_whole_tree_regardless_of_cwd(tmp_path, monkeypatch):
    package, root, sha = _seed_nested_repo(tmp_path)
    monkeypatch.setattr(run_model_backed_a, "_repo_root", lambda: str(root))
    monkeypatch.chdir(package)

    paths = run_model_backed_a._git_paths(sha)

    # Regression: called from inside experiments/semantic_atlas this used to
    # collapse to the package's own markdown files only.
    assert len(paths) == 3
    assert "papers/a.md" in paths
    assert "papers/b.md" in paths
    assert "experiments/semantic_atlas/README.md" in paths
    assert not any(path.endswith(".txt") for path in paths)


def test_git_paths_keeps_frozen_path_hash_ordering(tmp_path, monkeypatch):
    _, root, sha = _seed_nested_repo(tmp_path)
    monkeypatch.setattr(run_model_backed_a, "_repo_root", lambda: str(root))

    paths = run_model_backed_a._git_paths(sha)
    again = run_model_backed_a._git_paths(sha)

    expected = sorted(paths, key=lambda path: hashlib.sha256(path.encode()).hexdigest())
    assert paths == expected == again


def test_git_text_reads_root_relative_paths_from_any_cwd(tmp_path, monkeypatch):
    package, root, sha = _seed_nested_repo(tmp_path)
    monkeypatch.setattr(run_model_backed_a, "_repo_root", lambda: str(root))
    monkeypatch.chdir(package)

    text = run_model_backed_a._git_text(sha, "papers/a.md", limit=120)

    assert text.startswith("# a.md")