"""One-click launcher for SahakarSeva.

Run from Antigravity with `main.py` or double-click START.bat.
The launcher prepares the Python environment, creates the MySQL database if
needed, creates any missing tables, seeds demo data only for an empty DB, and
starts the mobile-first Flask app on the LAN.
"""
from __future__ import annotations
import os
import shutil
import socket
import stat
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# Resolve project root dynamically so the project runs out-of-the-box on any host, user profile, or drive.
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT = Path(ROOT_DIR)
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
REQ = ROOT / "requirements.txt"
QR_FILE = ROOT / "mobile_access_qr.png"
REQ_MARKER = ROOT / ".requirements_installed"


CRITICAL_MODULES = [
    "flask",
    "flask_login",
    "flask_sqlalchemy",
    "flask_socketio",
    "sqlalchemy",
    "pyotp",
    "qrcode",
    "mysql.connector",
    "requests",
    "reportlab",
]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("[SahakarSeva]", " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT_DIR, check=check)


def _handle_remove_readonly(func, path, exc_info):
    """Error handler for shutil.rmtree on Windows to clear read-only permissions."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def remove_venv_and_marker(venv_path: Path, marker_path: Path) -> None:
    """Safely remove a stale or broken virtual environment and its installation marker."""
    try:
        if marker_path.exists():
            marker_path.unlink(missing_ok=True)
    except Exception as exc:
        print(f"[SahakarSeva] Notice: could not remove marker {marker_path}: {exc}")

    if not venv_path.exists():
        return

    print(f"[SahakarSeva] Removing broken/stale virtual environment: {venv_path}")
    for attempt in range(3):
        try:
            if venv_path.is_dir():
                shutil.rmtree(venv_path, onerror=_handle_remove_readonly)
            else:
                venv_path.unlink(missing_ok=True)
            if not venv_path.exists():
                print("[SahakarSeva] Stale virtual environment removed successfully.")
                break
        except Exception as exc:
            if attempt == 2:
                print(f"[SahakarSeva] Warning: error removing virtual environment directory: {exc}")
            time.sleep(0.4)


def check_pyvenv_cfg(cfg_path: Path) -> bool:
    """Validate that base interpreter paths in pyvenv.cfg exist on this machine.

    Returns False if pyvenv.cfg points to a non-existent directory or executable
    from another host/user profile (e.g. C:\\Users\\Roshan\\...).
    """
    if not cfg_path.is_file():
        return False

    config: dict[str, str] = {}
    try:
        with open(cfg_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                config[key.strip().lower()] = val.strip()
    except Exception as exc:
        print(f"[SahakarSeva] Notice: could not read {cfg_path}: {exc}")
        return False

    # Check 'home' path if present
    home = config.get("home")
    if home and not os.path.exists(home):
        print(f"[SahakarSeva] pyvenv.cfg references non-existent base path: {home}")
        return False

    # Check 'executable' path if present
    executable = config.get("executable")
    if executable and not os.path.exists(executable):
        print(f"[SahakarSeva] pyvenv.cfg references non-existent interpreter: {executable}")
        return False

    return True


def is_python_executable_valid(python_path: Path) -> bool:
    """Test whether python_path can be successfully invoked by the current host runtime."""
    if not python_path.is_file():
        return False

    try:
        res = subprocess.run(
            [str(python_path), "-c", "import sys; sys.exit(0)"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode != 0:
            return False

        combined = (res.stderr or "") + (res.stdout or "")
        if "cannot find the path specified" in combined or "did not find executable" in combined:
            return False

        return True
    except (OSError, subprocess.SubprocessError, Exception) as exc:
        print(f"[SahakarSeva] Incompatible virtual environment python: {exc}")
        return False


def ensure_venv() -> None:
    """Ensure a healthy, functional virtual environment tailored to the current host."""
    cfg_file = VENV / "pyvenv.cfg"
    needs_recreate = False

    if not VENV.exists():
        print("\n[SahakarSeva] First run on this system: setting up Python environment...")
        needs_recreate = True
    elif not check_pyvenv_cfg(cfg_file):
        print("\n[SahakarSeva] Stale virtual environment detected (points to another host or user profile).")
        needs_recreate = True
    elif not is_python_executable_valid(PYTHON):
        print("\n[SahakarSeva] Virtual environment python is not executable on this machine.")
        needs_recreate = True

    if needs_recreate:
        remove_venv_and_marker(VENV, REQ_MARKER)

        print(f"[SahakarSeva] Creating fresh virtual environment using host interpreter:\n  {sys.executable}")
        run([sys.executable, "-m", "venv", str(VENV)])

        # Verify the newly created venv python
        if not is_python_executable_valid(PYTHON):
            print("\n" + "!" * 72)
            print("  [SahakarSeva] ERROR: Newly created virtual environment failed validation.")
            print(f"  Host Python: {sys.executable}")
            print(f"  Virtualenv Python: {PYTHON}")
            print("!" * 72 + "\n")
            raise SystemExit(1)

        print("[SahakarSeva] Virtual environment created successfully.")

        # Ensure and upgrade pip
        print("[SahakarSeva] Upgrading pip in virtual environment...")
        try:
            subprocess.run(
                [str(PYTHON), "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check"],
                capture_output=True,
                check=False
            )
        except Exception:
            pass
    else:
        # Quick check that pip is installed
        test_pip = subprocess.run([str(PYTHON), "-m", "pip", "--version"], capture_output=True)
        if test_pip.returncode != 0:
            print("[SahakarSeva] Ensuring pip in virtual environment...")
            subprocess.run([str(PYTHON), "-m", "ensurepip", "--default-pip"], check=False)


def check_venv_dependencies() -> bool:
    """Check whether all critical dependencies can be imported in .venv."""
    if not PYTHON.exists():
        return False
    if Path(sys.executable).resolve() == PYTHON.resolve():
        for m in CRITICAL_MODULES:
            try:
                __import__(m)
            except Exception:
                return False
        return True

    test_code = (
        "import sys\n"
        f"mods = {CRITICAL_MODULES!r}\n"
        "for m in mods:\n"
        "    try:\n"
        "        __import__(m)\n"
        "    except Exception:\n"
        "        sys.exit(1)\n"
        "sys.exit(0)\n"
    )
    try:
        res = subprocess.run([str(PYTHON), "-c", test_code], capture_output=True)
        return res.returncode == 0
    except Exception:
        return False


def verify_mysql_connector() -> bool:
    """Explicitly verify that mysql.connector is importable in .venv."""
    if not PYTHON.exists():
        return False
    if Path(sys.executable).resolve() == PYTHON.resolve():
        try:
            __import__("mysql.connector")
            return True
        except Exception:
            return False
    try:
        res = subprocess.run([str(PYTHON), "-c", "import mysql.connector"], capture_output=True)
        return res.returncode == 0
    except Exception:
        return False


def ensure_requirements() -> None:
    """Install dependencies into .venv when needed.

    The marker is never blindly trusted. Even if .requirements_installed exists,
    we verify that .venv can import all required packages (especially mysql.connector).
    If any dependency is missing, automatic installation/repair is executed.
    """
    if REQ_MARKER.exists():
        if check_venv_dependencies():
            return
        print("[SahakarSeva] Missing packages detected in virtual environment despite marker.")
        print("[SahakarSeva] Repairing virtual environment dependencies...\n")
        try:
            REQ_MARKER.unlink(missing_ok=True)
        except Exception:
            pass
    else:
        if check_venv_dependencies():
            REQ_MARKER.write_text("ok\n", encoding="utf-8")
            return
        print("\n[SahakarSeva] Checking required Python dependencies...")

    if not REQ.exists():
        print(f"\n[SahakarSeva] ERROR: requirements.txt not found at {REQ}")
        raise SystemExit(1)

    print("[SahakarSeva] Installing required packages into .venv (first run/repair)...\n")
    pip_cmd = [str(PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQ)]
    try:
        run(pip_cmd)
    except subprocess.CalledProcessError:
        print("\n" + "!" * 72)
        print("  [SahakarSeva] ERROR: Failed to install Python dependencies into .venv.")
        print(f"  Command failed: {' '.join(pip_cmd)}")
        print("  Please check your internet connection and file permissions.")
        print("!" * 72 + "\n")
        raise SystemExit(1) from None

    # Verify mysql.connector specifically as required
    print("[SahakarSeva] Verifying mysql.connector import in .venv...")
    verify_res = subprocess.run(
        [str(PYTHON), "-c", "import mysql.connector; print('[SahakarSeva] mysql.connector import successful.')"],
        capture_output=True,
        text=True
    )
    if verify_res.returncode != 0:
        print("\n" + "!" * 72)
        print("  [SahakarSeva] ERROR: mysql-connector-python failed to import after installation.")
        if verify_res.stderr:
            print(f"  Details: {verify_res.stderr.strip()}")
        print("!" * 72 + "\n")
        raise SystemExit(1) from None
    else:
        if verify_res.stdout.strip():
            print(verify_res.stdout.strip())

    if not check_venv_dependencies():
        print("\n" + "!" * 72)
        print("  [SahakarSeva] ERROR: Dependency verification failed after installation.")
        print("!" * 72 + "\n")
        raise SystemExit(1) from None

    print("[SahakarSeva] Dependencies verified.")
    REQ_MARKER.write_text("ok\n", encoding="utf-8")


def mysql_settings() -> tuple[str, int, str, str, str]:
    from config import Config
    return Config.MYSQL_HOST, Config.MYSQL_PORT, Config.MYSQL_USER, Config.MYSQL_PASSWORD, Config.MYSQL_DATABASE


def ensure_mysql_database() -> None:
    """Create the configured MySQL database without touching existing data."""
    if not verify_mysql_connector():
        print("[SahakarSeva] mysql.connector missing before database check. Repairing...")
        ensure_requirements()

    import mysql.connector
    host, port, user, password, database = mysql_settings()
    print(f"[SahakarSeva] Checking MySQL at {host}:{port} ...")
    try:
        # Explicitly use legacy MySQL UTF-8. This works on older MySQL/MariaDB
        # versions that do not know the newer utf8mb4 character set.
        conn = mysql.connector.connect(
            host=host, port=port, user=user, password=password, charset="utf8"
        )
    except mysql.connector.Error as first_exc:
        # Some local XAMPP/MySQL installs use root with no password. Try that
        # automatically before showing an error; no manual SQL/copy-paste needed.
        if user == "root" and password == "root":
            try:
                conn = mysql.connector.connect(host=host, port=port, user=user, password="", charset="utf8")
                os.environ["MYSQL_PASSWORD"] = ""
                print("[SahakarSeva] MySQL root account accepted without a password.")
            except mysql.connector.Error:
                raise RuntimeError(
                    "Could not connect to MySQL. Start MySQL and check your local "
                    "root password in the project settings.\n"
                    f"MySQL said: {first_exc}"
                ) from first_exc
        else:
            raise RuntimeError(
                "Could not connect to MySQL. Start MySQL and check the "
                "MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD settings.\n"
                f"MySQL said: {first_exc}"
            ) from first_exc

    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database}` "
            "CHARACTER SET utf8 COLLATE utf8_unicode_ci"
        )
        cur.close()
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        raise
    print(f"[SahakarSeva] MySQL database ready: {database}")


def ensure_schema_and_demo_data() -> None:
    """Use SQLAlchemy to create missing tables and seed only an empty DB."""
    if not verify_mysql_connector():
        print("[SahakarSeva] mysql.connector missing before running seed_db.py. Repairing...")
        ensure_requirements()

    print("[SahakarSeva] Checking database tables...")
    run([str(PYTHON), "seed_db.py"])


def lan_ip() -> str:
    ip = "127.0.0.1"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
    except OSError:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except OSError:
            pass
    return ip


def make_qr(url: str) -> None:
    try:
        import qrcode
        qrcode.make(url).save(QR_FILE)
        print(f"[SahakarSeva] Phone QR: {QR_FILE}")
    except Exception as exc:
        print(f"[SahakarSeva] QR skipped: {exc}")


def open_browser(url: str) -> None:
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main() -> int:
    os.chdir(ROOT_DIR)
    ensure_venv()

    # If launched with an external/system Python, ensure requirements and re-launch
    # with .venv python so that all runtime code (Flask app, SQLAlchemy, background
    # jobs) executes strictly inside the isolated virtual environment.
    if Path(sys.executable).resolve() != PYTHON.resolve():
        ensure_requirements()
        try:
            res = subprocess.run([str(PYTHON), str(ROOT / "main.py")] + sys.argv[1:])
            return res.returncode
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            print(f"[SahakarSeva] Virtual environment launcher error: {exc}")
            return 1

    ensure_requirements()

    # MySQL is the single source of truth for this project.
    ensure_mysql_database()
    ensure_schema_and_demo_data()

    ip = lan_ip()
    local_url = "http://127.0.0.1:5000"
    phone_url = f"http://{ip}:5000"

    print("\n" + "=" * 72)
    print("  SahakarSeva is ready")
    print("=" * 72)
    print(f"  Laptop: {local_url}")
    print(f"  Phone : {phone_url}")
    print("  MySQL : connected")
    print("  Same app on phone, laptop and desktop")
    print("=" * 72 + "\n")

    make_qr(phone_url)
    open_browser(local_url)

    from app import app, socketio
    time.sleep(0.4)
    try:
        socketio.run(app, debug=False, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n[SahakarSeva] Server stopped.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())