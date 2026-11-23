import subprocess
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from . import git_sync


def git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=cwd, capture_output=True, text=True, check=True,
    ).stdout


class PushFilesTests(SimpleTestCase):
    """_push runs on the live checkout, so it must push uploads and never
    change the code that is on disk."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.remote = root / "remote.git"
        self.server = root / "server"
        git(root, "init", "-q", "--bare", "-b", "main", str(self.remote))
        git(root, "clone", "-q", str(self.remote), str(self.server))
        (self.server / "views.py").write_text("old code\n")
        git(self.server, "add", "views.py")
        git(self.server, "commit", "-q", "-m", "start")
        git(self.server, "push", "-q", "origin", "HEAD:main")

        settings = override_settings(BASE_DIR=self.server)
        settings.enable()
        self.addCleanup(settings.disable)

    def upload(self, name):
        path = self.server / "media" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"image")
        git_sync._push([f"media/{name}"], f"Afbeelding toegevoegd: {name}")

    def test_upload_reaches_github(self):
        self.upload("a.jpg")
        self.assertIn("media/a.jpg", git(self.remote, "ls-tree", "-r", "--name-only", "main"))
        self.assertIn("Gepusht", git_sync.recent_log()[0])

    def test_newer_github_commits_do_not_change_live_code(self):
        other = self.server.parent / "other"
        git(other.parent, "clone", "-q", str(self.remote), str(other))
        (other / "views.py").write_text("new code\n")
        git(other, "commit", "-q", "-am", "new code")
        git(other, "push", "-q", "origin", "HEAD:main")

        with self.assertLogs("gallery.git_sync", "ERROR"):
            self.upload("b.jpg")

        self.assertEqual((self.server / "views.py").read_text(), "old code\n")
        self.assertIn("Afbeelding toegevoegd: b.jpg", git(self.server, "log", "-1", "--format=%s"))
        self.assertIn("FOUT", git_sync.recent_log()[0])
