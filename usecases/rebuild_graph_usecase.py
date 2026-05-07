import os
import subprocess
import shutil
import requests
import zipfile
import tempfile

from services.gtfs_service import GTFSService


class RebuildGraphUseCase:
    def __init__(self, db, otp_db, user_id):
        self.db = db
        self.otp_db = otp_db
        self.user_id = user_id

        # Local repo path (your machine for now)
        self.deploy_repo_path = r"C:\TaxiMelaProject\taximela-otp-deploy"
        self.branch = "otp-deploy-clean"
        self.gtfs_path = os.path.join(self.deploy_repo_path, "data", "gtfs")

    def execute(self):
        print(f"🚀 Starting graph rebuild by {self.user_id}")

        zip_path = self.export_gtfs()
        self.update_repo_gtfs(zip_path)
        self.commit_and_push()
        self.trigger_render_deploy()

        print("✅ Full pipeline completed.")

    # 1. EXPORT GTFS
    def export_gtfs(self):
        print("📦 Exporting GTFS...")

        service = GTFSService(self.otp_db)
        zip_data = service.export_zip()

        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.write(zip_data)
        temp_zip.close()

        print(f"📦 GTFS zip created: {temp_zip.name}")
        return temp_zip.name

    # 2. UPDATE REPO FILES
    def update_repo_gtfs(self, zip_path):
        print("📂 Updating GTFS in repo...")

        if os.path.exists(self.gtfs_path):
            shutil.rmtree(self.gtfs_path)

        os.makedirs(self.gtfs_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.gtfs_path)

        print(f"📂 GTFS extracted to {self.gtfs_path}")

    # 3. GIT COMMIT + PUSH
    def commit_and_push(self):
        print("🔧 Committing GTFS only...")

        def run(cmd):
            result = subprocess.run(
                cmd,
                cwd=self.deploy_repo_path,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            print(result.stderr)
            if result.returncode != 0:
                raise Exception(f"Git command failed: {' '.join(cmd)}")

        run(["git", "pull", "origin", self.branch])
        run(["git", "add", "data/gtfs"])

        commit = subprocess.run(
            ["git", "commit", "-m", "Update GTFS data"],
            cwd=self.deploy_repo_path,
            capture_output=True,
            text=True
        )

        if "nothing to commit" in (commit.stdout + commit.stderr).lower():
            print("⚠️ No GTFS changes detected.")
            return

        print(commit.stdout)
        print(commit.stderr)

        run(["git", "push", "origin", self.branch])
        print("📤 Pushed GTFS to otp-deploy-clean")

    # 4. TRIGGER RENDER DEPLOY
    def trigger_render_deploy(self):
        print("🚀 Triggering Render deploy...")

        response = requests.post(
            "https://api.render.com/deploy/srv-d70088fkijhs73d41h00?key=mLVbAyCll8Q"
        )

        if response.status_code == 200:
            print("✅ Render deploy triggered")
        else:
            print("❌ Render deploy failed:", response.text)