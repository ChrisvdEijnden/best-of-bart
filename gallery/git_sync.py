"""Commit uploaded files and push them to GitHub in the background."""
import logging
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)
_lock = threading.Lock()


class GitSyncError(Exception):
    pass


def log_file():
    return Path(settings.BASE_DIR) / "git_sync.log"


def recent_log(lines=20):
    try:
        return log_file().read_text(encoding="utf-8").splitlines()[-lines:][::-1]
    except FileNotFoundError:
        return []


def push_files(paths, message):
    """Push the given files to GitHub once the current database transaction commits."""
    if not getattr(settings, "GIT_AUTO_PUSH", False):
        return
    base = Path(settings.BASE_DIR).resolve()
    relative = [str(Path(p).resolve().relative_to(base)) for p in paths]
    transaction.on_commit(
        lambda: threading.Thread(target=_push, args=(relative, message), daemon=True).start()
    )


def _write_log(line):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with log_file().open("a", encoding="utf-8") as f:
        f.write(f"{stamp}  {line}\n")


def _git(*args, check=True):
    result = subprocess.run(
        ["git", *args], cwd=settings.BASE_DIR, capture_output=True, text=True, timeout=300
    )
    if check and result.returncode != 0:
        raise GitSyncError(f"git {args[0]}: {(result.stderr or result.stdout).strip()}")
    return result


def _push(paths, message):
    remote = settings.GIT_AUTO_PUSH_REMOTE
    branch = settings.GIT_AUTO_PUSH_BRANCH
    name, email = settings.GIT_AUTO_PUSH_AUTHOR
    with _lock:
        try:
            _git("add", "--", *paths)
            if _git("diff", "--cached", "--quiet", "--", *paths, check=False).returncode == 0:
                _write_log(f"Al op GitHub: {message}")
                return
            _git("-c", f"user.name={name}", "-c", f"user.email={email}",
                 "commit", "--only", "-m", message, "--", *paths)

            # Never fetch or rebase here: the live site runs from this checkout,
            # so that would put new code live without migrate or a restart.
            # The commit stays here and goes along with the next push after a
            # normal deploy (git pull).
            if _git("push", remote, f"HEAD:{branch}", check=False).returncode != 0:
                raise GitSyncError(
                    "GitHub heeft nieuwere commits; commit staat klaar op de server "
                    "en wordt gepusht na de volgende deploy."
                )

            _write_log(f"Gepusht: {message}")
        except Exception as e:
            logger.exception("Pushing %s to GitHub failed", paths)
            _write_log(f"FOUT bij '{message}': {e}")
