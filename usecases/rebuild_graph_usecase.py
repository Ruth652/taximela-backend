import os
import subprocess
import shutil
from wsgiref import headers
import requests
import zipfile
import tempfile

from services.gtfs_service import GTFSService


class RebuildGraphUseCase:
    def __init__(self, db, otp_db, user_id):
        self.db = db
        self.otp_db = otp_db
        self.user_id = user_id
        self.GITHUB_REPO = "https://github.com/Ruth652/taximela-backend.git"

        # Local repo path (your machine for now)
        # self.deploy_repo_path = r"C:\TaxiMelaProject\taximela-otp-deploy"
        # self.branch = "otp-deploy-clean"
        # self.gtfs_path = os.path.join(self.deploy_repo_path, "data", "gtfs")

    def execute(self):
        print(f"🚀 Starting graph rebuild by {self.user_id}")

        zip_path = self.export_gtfs()
        self.commit_and_push(zip_path)

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
    # def update_repo_gtfs(self, zip_path):
    #     print("📂 Updating GTFS in repo...")

    #     if os.path.exists(self.gtfs_path):
    #         shutil.rmtree(self.gtfs_path)

    #     os.makedirs(self.gtfs_path, exist_ok=True)

    #     with zipfile.ZipFile(zip_path, "r") as zip_ref:
    #         zip_ref.extractall(self.gtfs_path)

    #     print(f"📂 GTFS extracted to {self.gtfs_path}")

    # 3. GIT COMMIT + PUSH
    def commit_and_push(self, zip_path):
        print("🔧 Cloning repo...")

        repo_dir = tempfile.mkdtemp()

        subprocess.run([
            "git", "clone",
            "--branch", "otp-deploy-clean",
            self.GITHUB_REPO,
            repo_dir
        ], check=True)

        gtfs_path = os.path.join(repo_dir, "data", "gtfs")

        print("📂 Replacing GTFS...")

        if os.path.exists(gtfs_path):
            shutil.rmtree(gtfs_path)

        os.makedirs(gtfs_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(gtfs_path)

        print("💾 Committing changes...")

        subprocess.run(["git", "add", "data/gtfs"], cwd=repo_dir, check=True)

        result = subprocess.run(
            ["git", "commit", "-m", "Update GTFS data"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if "nothing to commit" in (result.stdout + result.stderr).lower():
            print("⚠️ No changes")
            shutil.rmtree(repo_dir)
            return

        result = subprocess.run(
            ["git", "push", "origin", "otp-deploy-clean"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        if result.returncode != 0:
            raise Exception(
                f"Git push failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
        
                print("🚀 Pushed → Railway will auto-deploy")

        shutil.rmtree(repo_dir)
    # 4. TRIGGER RAILWAY DEPLOY
    # def trigger_railway_deploy(self):
    #     print("🚀 Triggering Railway deploy...")

    #     headers = {
    #     "Authorization": f"Bearer {RAILWAY_TOKEN}",
    #     "Content-Type": "application/json"
    # }

    #     response = requests.post(
    #         "RAILWAY_DEPLOYMENT_ENDPOINT",
    #         headers=headers,
    #         json={
    #             "project_id": "your_project_id",
    #             "environment_id": "your_environment_id",
    #             "service_id": "your_service_id"
    #         }
    #     )
    #     if response.status_code == 200:
    #         print("✅ Railway deploy triggered")
    #     else:
    #         print("❌ Railway deploy failed:", response.text)
