import os
import json
import logging
import tempfile
import requests
from github import Github
import git
from .errors import AppError


logging.basicConfig(level=logging.DEBUG)


class ConfigManager:
    def __init__(
        self, repo_url, git_api_token=None, github_client=None, git_client=None
    ):
        self.config_dir = tempfile.TemporaryDirectory().name
        self.repo_url = repo_url
        self.git_api_token = git_api_token
        self.config_cache = {}
        self.github_client = github_client or Github(self.git_api_token)
        self.git_client = git_client or git.Git()
        self.set_clone_url()
        self.clone_and_populate_cache()

    def clone_and_populate_cache(self):
        self.clone_repository()
        self.populate_cache()

    def set_clone_url(self):
        if self.git_api_token:
            self.clone_url = self.repo_url.replace(
                "https://", f"https://{self.git_api_token}@"
            )
        else:
            self.clone_url = self.repo_url

    def test_github_access(self):
        # test with token
        if self.git_api_token:
            headers = {"Authorization": f"Bearer {self.git_api_token}"}
            response = requests.get("https://api.github.com/user", headers=headers)
            return response.status_code == 200
        # test without token
        else:
            response = requests.get(self.clone_url)
            return response.status_code == 200

    def clone_repository(self):
        logging.debug(
            f"Cloning git repository from {self.clone_url} to {self.config_dir}"
        )
        if not self.test_github_access():
            raise AppError(
                "Can't access repository, check token or if private repo",
                status_code=401,
            )
        try:
            self.git_client.clone(self.clone_url, self.config_dir)
        except git.exc.GitCommandError as err:
            raise AppError(
                "Could not clone the git repository", status_code=500, error=err
            ) from err

    def populate_cache(self):
        """
        Populate the config cache with the config files from the config directory
        """
        self.config_cache = {}
        for entry in os.scandir(self.config_dir):
            if entry.is_dir() and os.path.isfile(
                os.path.join(entry.path, "config.json")
            ):
                config = self.load_json_file(os.path.join(entry.path, "config.json"))
                if config and self.validate_config(config):
                    self.config_cache[entry.name] = config

    def validate_config(self, config):
        """
        Validate the structure of a configuration
        """
        for setting, properties in config.items():
            if not all(key in properties for key in ["value", "enabled", "type"]):
                return False
        return True

    def load_json_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                config_data = json.load(f)
                if len(json.dumps(config_data)) > 100000:
                    raise AppError("Config file too large")
                return config_data
        except Exception as err:
            logging.error(f"Unexpected error: {err}")
            return {}

    def get_config(self, service_name):
        return self.config_cache.get(service_name, {})

    def refresh_configs(self):
        try:
            git_repo = git.cmd.Git(self.config_dir)
            git_repo.pull()
            self.populate_cache()
            return True
        except git.exc.GitCommandError as giterr:
            raise AppError(
                "Could not pull the git repository", status_code=500, error=giterr
            ) from giterr
        except Exception as err:
            raise AppError(
                "Unexpected error occurred", status_code=500, error=err
            ) from err

    def update_config(self, service_name, setting_name, property_name, new_value):
        config = self.config_cache.get(service_name)
        if not config or setting_name not in config:
            return False

        config[setting_name][property_name] = new_value
        self.config_cache[service_name] = config
        return True
