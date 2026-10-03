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

            if _git("push", remote, f"HEAD:{branch}", check=False).returncode != 0:
                # GitHub has newer commits: replay ours on top, unless that
                # would overwrite files that were changed here on the server.
                _git("fetch", remote, branch)
                incoming = set(_git("diff", "--name-only", "HEAD...FETCH_HEAD").stdout.split())
                dirty = {line[3:] for line in _git("status", "--porcelain").stdout.splitlines()}
                if incoming & dirty:
                    raise GitSyncError(
                        "GitHub heeft nieuwere versies van " + ", ".join(sorted(incoming & dirty))
                        + "; commit staat klaar op de server, push handmatig."
                    )
                _git("rebase", "--autostash", "FETCH_HEAD")
                _git("push", remote, f"HEAD:{branch}")

            _write_log(f"Gepusht: {message}")
        except Exception as e:
            logger.exception("Pushing %s to GitHub failed", paths)
            _write_log(f"FOUT bij '{message}': {e}")
