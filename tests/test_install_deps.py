import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_deps.sh"
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"
WARMUP_SCRIPT = REPO_ROOT / "scripts" / "warmup_hybrid_models.py"


class InstallDepsScriptTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._tmpdir.name) / "repo"
        (self.repo_root / "scripts").mkdir(parents=True)

        shutil.copy2(INSTALL_SCRIPT, self.repo_root / "scripts" / "install_deps.sh")
        shutil.copy2(REQUIREMENTS_FILE, self.repo_root / "requirements.txt")

        if WARMUP_SCRIPT.exists():
            shutil.copy2(WARMUP_SCRIPT, self.repo_root / "scripts" / "warmup_hybrid_models.py")

        self.log_path = self.repo_root / "calls.log"
        self.stub_dir = self.repo_root / "stubs"
        self.stub_dir.mkdir()
        self._write_fake_python()
        self._write_fake_java()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_executable(self, name: str, content: str) -> None:
        path = self.stub_dir / name
        path.write_text(content)
        path.chmod(path.stat().st_mode | stat.S_IEXEC)

    def _write_fake_python(self) -> None:
        self._write_executable(
            "python3",
            """#!/usr/bin/env bash
set -euo pipefail
printf 'python %s\n' "$*" >> "${FAKE_LOG_FILE:?}"
if [ "${1:-}" = "-m" ] && [ "${2:-}" = "venv" ]; then
  venv_dir="${3:?}"
  mkdir -p "$venv_dir/bin"
  cat > "$venv_dir/bin/pip" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf 'venv-pip %s\n' "$*" >> "${FAKE_LOG_FILE:?}"
EOF
  chmod +x "$venv_dir/bin/pip"
  cat > "$venv_dir/bin/python" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf 'venv-python %s\n' "$*" >> "${FAKE_LOG_FILE:?}"
EOF
  chmod +x "$venv_dir/bin/python"
fi
""",
        )
        shutil.copy2(self.stub_dir / "python3", self.stub_dir / "python")
        (self.stub_dir / "python").chmod((self.stub_dir / "python").stat().st_mode | stat.S_IEXEC)

    def _write_fake_java(self) -> None:
        self._write_executable(
            "java",
            """#!/usr/bin/env bash
set -euo pipefail
printf 'java %s\n' "$*" >> "${FAKE_LOG_FILE:?}"
""",
        )

    def _run_install(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["FAKE_LOG_FILE"] = str(self.log_path)
        env["PATH"] = f"{self.stub_dir}:/usr/bin:/bin"
        env["HOME"] = str(self.repo_root / "home")
        return subprocess.run(
            ["bash", str(self.repo_root / "scripts" / "install_deps.sh")],
            cwd=self.repo_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_installs_hybrid_extras_and_warms_models(self) -> None:
        completed = self._run_install()

        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}",
        )

        calls = self.log_path.read_text().splitlines()

        self.assertTrue(
            any(line.startswith("python -m venv ") for line in calls),
            msg=f"missing venv creation in calls: {calls}",
        )
        self.assertTrue(
            any(
                line.startswith("venv-pip install opendataloader-pdf[hybrid]>=2.0")
                for line in calls
            ),
            msg=f"missing hybrid dependency install in calls: {calls}",
        )
        self.assertTrue(
            any("warmup_hybrid_models.py" in line for line in calls),
            msg=f"missing hybrid warmup invocation in calls: {calls}",
        )


if __name__ == "__main__":
    unittest.main()
