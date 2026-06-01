import os
import subprocess
import shutil
import zipfile
import tempfile

from services.gtfs_service import GTFSService


class RebuildGraphUseCase:

    def __init__(self, db, otp_db, user_id):
        # GitHub token from Render environment
        token = os.environ["GITHUB_TOKEN"]

        self.db = db
        self.otp_db = otp_db
        self.user_id = user_id

        # Authenticated repo URL for clone + push
        self.GITHUB_REPO = (
            f"https://{token}@github.com/Ruth652/taximela-backend.git"
        )

    def execute(self):
        print(f"🚀 Starting graph rebuild by {self.user_id}")

        # Step 1: Export GTFS from DB as zip
        zip_path = self.export_gtfs()

        # Step 2: Clone repo → update files → commit → push
        self.commit_and_push(zip_path)

        print("✅ Full pipeline completed.")

    def export_gtfs(self):
        """Generate GTFS zip from database"""
        print("📦 Exporting GTFS...")

        service = GTFSService(self.otp_db)
        zip_data = service.export_zip()

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.write(zip_data)
        temp_zip.close()

        print(f"📦 GTFS zip created: {temp_zip.name}")
        return temp_zip.name

    def commit_and_push(self, zip_path):
        """Clone repo, replace GTFS, commit changes, push to GitHub"""

        # Prevent Git from waiting for username/password prompts
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        print("🔧 Cloning repo...")

        repo_dir = tempfile.mkdtemp()

        # Clone OTP deployment branch
        clone = subprocess.run(
            [
                "git", "clone",
                "--branch", "otp-deploy-clean",
                self.GITHUB_REPO,
                repo_dir
            ],
            capture_output=True,
            text=True,
            env=env
        )

        print("CLONE STDOUT:\n", clone.stdout)
        print("CLONE STDERR:\n", clone.stderr)

        if clone.returncode != 0:
            raise Exception("Git clone failed")

        gtfs_path = os.path.join(repo_dir, "data", "gtfs")

        print("📂 Replacing GTFS data...")

        # Remove old GTFS
        if os.path.exists(gtfs_path):
            shutil.rmtree(gtfs_path)

        os.makedirs(gtfs_path, exist_ok=True)

        # Extract new GTFS
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(gtfs_path)

        print("📊 Staging changes...")

        # IMPORTANT: stage ALL changes (new, modified, deleted)
        subprocess.run(
            ["git", "add", "-A", "data/gtfs"],
            cwd=repo_dir,
            check=True
        )

        # Set Git identity (REQUIRED in Render environments)
        subprocess.run(
            ["git", "config", "user.email", "render@bot.com"],
            cwd=repo_dir,
            check=True
        )

        subprocess.run(
            ["git", "config", "user.name", "Render Bot"],
            cwd=repo_dir,
            check=True
        )

        print("💾 Committing changes...")

        commit = subprocess.run(
            ["git", "commit", "-m", "Update GTFS data"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        print("COMMIT STDOUT:\n", commit.stdout)
        print("COMMIT STDERR:\n", commit.stderr)

        # If nothing changed, stop early
        if "nothing to commit" in (commit.stdout + commit.stderr).lower():
            print("⚠️ No changes detected — skipping push")
            shutil.rmtree(repo_dir)
            return

        print("🚀 Pushing to GitHub...")

        push = subprocess.run(
            ["git", "push", "origin", "otp-deploy-clean"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            env=env
        )

        print("PUSH STDOUT:\n", push.stdout)
        print("PUSH STDERR:\n", push.stderr)

        if push.returncode != 0:
            raise Exception(
                f"Git push failed\nSTDOUT:\n{push.stdout}\nSTDERR:\n{push.stderr}"
            )

        print("🚀 Pushed successfully → Railway will auto-deploy")

        # Cleanup temp repo
        shutil.rmtree(repo_dir)