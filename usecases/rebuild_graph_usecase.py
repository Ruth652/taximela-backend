import os
import subprocess
import shutil
import zipfile
import tempfile

from services.gtfs_service import GTFSService


class RebuildGraphUseCase:

    def __init__(self, db, otp_db, user_id):
        token = os.environ["GITHUB_TOKEN"]

        self.db = db
        self.otp_db = otp_db
        self.user_id = user_id

        self.GITHUB_REPO = (
            f"https://{token}@github.com/Ruth652/taximela-backend.git"
        )

    def execute(self):
        print(f"🚀 Starting graph rebuild by {self.user_id}")

        zip_path = self.export_gtfs()
        self.commit_and_push(zip_path)

        print("✅ Full pipeline completed.")

    def export_gtfs(self):
        print("📦 Exporting GTFS...")

        service = GTFSService(self.otp_db)
        zip_data = service.export_zip()

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.write(zip_data)
        temp_zip.close()

        print(f"📦 GTFS zip created: {temp_zip.name}")
        return temp_zip.name

    def commit_and_push(self, zip_path):

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        print("🔧 Cloning repo...")

        repo_dir = tempfile.mkdtemp()

        # ✅ IMPORTANT FIX: use env here
        clone = subprocess.run(
            [
                "git", "clone",
                "--branch", "otp-deploy-clean",
                self.GITHUB_REPO,
                repo_dir
            ],
            capture_output=True,
            text=True,
            env=env   # <<< THIS WAS MISSING BEFORE
        )

        print("STDOUT:\n", clone.stdout)
        print("STDERR:\n", clone.stderr)

        if clone.returncode != 0:
            raise Exception("Git clone failed")

        gtfs_path = os.path.join(repo_dir, "data", "gtfs")

        print("📂 Replacing GTFS...")

        if os.path.exists(gtfs_path):
            shutil.rmtree(gtfs_path)

        os.makedirs(gtfs_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(gtfs_path)

        print("💾 Committing changes...")

        subprocess.run(["git", "add", "data/gtfs"], cwd=repo_dir, check=True)

        commit = subprocess.run(
            ["git", "commit", "-m", "Update GTFS data"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if "nothing to commit" in (commit.stdout + commit.stderr).lower():
            print("⚠️ No changes")
            shutil.rmtree(repo_dir)
            return

        print("🚀 Pushing...")

        push = subprocess.run(
            ["git", "push", "origin", "otp-deploy-clean"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            env=env   # (good practice to include here too)
        )

        print("STDOUT:\n", push.stdout)
        print("STDERR:\n", push.stderr)

        if push.returncode != 0:
            raise Exception(
                f"Git push failed\nSTDOUT:\n{push.stdout}\nSTDERR:\n{push.stderr}"
            )

        print("🚀 Pushed → Railway will auto-deploy")

        shutil.rmtree(repo_dir)
