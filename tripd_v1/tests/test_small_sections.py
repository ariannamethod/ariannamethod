import importlib.util
import sys
import random
import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent

def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, BASE / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

memory = _load("tripd_pkg.tripd_memory", "tripd_memory.py")
expansion = _load("tripd_pkg.tripd_expansion", "tripd_expansion.py")
tripd = _load("tripd_pkg.tripd", "tripd.py")
TripDModel = tripd.TripDModel


def _extract_tripd_commands(script: str, model: TripDModel) -> list[str]:
    """Extract TRIPD command calls from a generated script."""
    # Get all known commands
    all_known_commands = model.all_commands + model.extra_verbs
    
    # Find function calls in the script
    tripd_commands = []
    lines = script.splitlines()
    
    for line in lines:
        line = line.strip()
        # Look for function calls that match known commands
        for cmd in all_known_commands:
            if cmd in line and line.endswith("()"):
                # Make sure it's actually the command and not part of a string/comment
                if not line.startswith('"') and not line.startswith('#'):
                    tripd_commands.append(cmd)
                    break
    
    return tripd_commands


@pytest.mark.parametrize("num_cmds", [1, 2, 3])
def test_generate_from_small_section(tmp_path, num_cmds):
    memory._LOG_PATH = tmp_path / "scripts.log"
    expansion._TRAIN_LOG = tmp_path / "train.log"
    dictionary = "## small\n" + "\n".join(f"cmd{i}()" for i in range(num_cmds))
    dictionary += "\n\n## pool\n" + "\n".join(f"pool{i}()" for i in range(4)) + "\n"
    path = tmp_path / "dict.md"
    path.write_text(dictionary)

    model = TripDModel(path)
    random.seed(0)
    script = model.generate_from_section("small")
    commands = _extract_tripd_commands(script, model)
    
    # With the new dynamic sizing, we expect 6-14 commands depending on metrics
    # For the simple test case, it should be at least 6 commands
    assert len(commands) >= 6
    
    # Check that the section commands are present
    for i in range(num_cmds):
        assert f"cmd{i}()" in commands
    
    # Should also have some from the pool when section is small
    if num_cmds < 6:
        assert any(f"pool{i}()" in commands for i in range(4))


@pytest.mark.parametrize("num_cmds", [1, 2, 3])
def test_generate_script_with_small_section(tmp_path, num_cmds):
    memory._LOG_PATH = tmp_path / "scripts.log"
    expansion._TRAIN_LOG = tmp_path / "train.log"

    dictionary = "## small\n" + "\n".join(f"cmd{i}()" for i in range(num_cmds))
    dictionary += "\n\n## pool\n" + "\n".join(f"pool{i}()" for i in range(4)) + "\n"
    path = tmp_path / "dict.md"
    path.write_text(dictionary)

    model = TripDModel(path)
    random.seed(0)
    model._choose_section = lambda metrics: "small"
    script = model.generate_script("msg")
    commands = _extract_tripd_commands(script, model)
    
    # With the new dynamic sizing, we expect 6-14 commands depending on metrics
    assert len(commands) >= 6
    
    # Check that the section commands are present  
    for i in range(num_cmds):
        assert f"cmd{i}()" in commands
    
    # Should also have some from global pool when section is small
    if num_cmds < 6:
        assert any(f"pool{i}()" in commands for i in range(4))
