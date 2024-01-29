import json
import sys
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound

class ProjectConfig:
    def __init__(self, project_id, secret_folders):
        self.project_id = project_id
        self.secret_folders = secret_folders

def main():
    if len(sys.argv) < 2:
        print("Please provide the project id as an argument")
        return

    project_id = sys.argv[1]
    projects, err = load_config("config.json")
    if err:
        print(f"Error loading config file: {err}")
        return

    secret_folders, found = get_secret_folders(project_id, projects)
    if not found:
        print("Project not found in the configuration")
        return

    delete_old_versions(secret_folders, project_id)

def load_config(filename):
    try:
        with open(filename, 'r') as config_file:
            projects = json.load(config_file)
            return [ProjectConfig(p['project-id'], p['secret-folders']) for p in projects], None
    except Exception as e:
        return None, f"Error loading config file: {e}"

def get_secret_folders(project_id, projects):
    for project in projects:
        if project.project_id == project_id:
            return project.secret_folders, True
    return None, False

def delete_old_versions(secret_folders, project_id):
    versions_to_keep = 2
    client = secretmanager.SecretManagerServiceClient()

    for secret_name in secret_folders:
        try:
            # Get all versions of the secret and sort them by create_time
            secret_path = f"projects/{project_id}/secrets/{secret_name}"
            versions = client.list_secret_versions(request={"parent": secret_path})
            versions = list(versions)
            versions.sort(key=lambda v: v.create_time, reverse=True)

            versions_to_delete = versions[versions_to_keep:]

            for version in versions_to_delete:
                version_name = version.name
                client.destroy_secret_version(request={"name": version_name})
                print(f"Destroyed version {version_name} of secret {secret_name}")
        except NotFound as e:
            print(f"Secret {secret_name} not found: {e}")
        except Exception as e:
            print(f"Error destroying versions for secret {secret_name}: {e}")

if __name__ == "__main__":
    main()
