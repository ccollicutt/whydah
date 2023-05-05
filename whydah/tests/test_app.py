import os
import json
import pytest
from whydah.config_manager import ConfigManager
from whydah.errors import AppError
from whydah.app import create_app


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


@pytest.fixture
def config_manager():
    repo_url = "https://github.com/ccollicutt/python-service-config-examples.git"
    manager = ConfigManager(repo_url)
    yield manager


def test_get_config(config_manager):
    config = config_manager.get_config("service1")
    assert config["feature1"] == "true"
    assert config["feature2"] == "true"
    assert config["feature3"] == "false"


def test_get_missing_config(config_manager):
    config = config_manager.get_config("nonexistent_service")
    assert config == {}


def test_populate_cache(config_manager):
    assert len(config_manager.config_cache) == 2
    assert "service1" in config_manager.config_cache
    assert "superservice" in config_manager.config_cache
    assert "noconfigjson" not in config_manager.config_cache
    assert "brokenjsonconfig" not in config_manager.config_cache


def test_refresh_configs(config_manager):
    # modify the config file for superservice
    config_file = os.path.join(config_manager.config_dir, "superservice/config.json")
    with open(config_file, "w") as f:
        json.dump({"feature1": "false", "feature2": "true", "feature3": "false"}, f)

    # refresh configs and check that the changes are reflected in the cache
    assert config_manager.refresh_configs() is True
    config = config_manager.get_config("superservice")
    assert config["feature1"] == "false"
    assert config["feature2"] == "true"
    assert config["feature3"] == "false"


def test_refresh_configs_error(config_manager):
    # change the config directory to a non-existent path to simulate a git error
    config_manager.config_dir = "/tmp/doesntexist"

    with pytest.raises(AppError) as e:
        config_manager.refresh_configs()

    assert e.value.status_code == 500


def test_get_all_configs(client):
    response = client.get("/config")
    assert response.status_code == 200
    assert set(response.json) == {"service1", "superservice"}

def test_update_config(config_manager):
    # Check initial values
    config = config_manager.get_config("service1")
    assert config["feature1"] == "true"

    # Update a setting
    success = config_manager.update_config("service1", "feature1", "false")
    assert success is True

    # Check if the setting is updated
    config = config_manager.get_config("service1")
    assert config["feature1"] == "false"

    # Test updating non-existent service and setting
    success = config_manager.update_config("nonexistent_service", "feature1", "false")
    assert success is False

    success = config_manager.update_config("service1", "nonexistent_setting", "false")
    assert success is False

def test_update_config_invalid_value(client):
    response = client.post("/config/service1/feature1", json={"value": ""})
    assert response.status_code == 400

    response = client.post("/config/service1/feature1", json={"value": 123})
    assert response.status_code == 400

def test_update_config_invalid_length(client):
    long_string = "a" * 1025
    response = client.post("/config/service1/feature1", json={"value": long_string})
    assert response.status_code == 400

def test_update_config_missing_value(client):
    response = client.post("/config/service1/feature1", json={})
    assert response.status_code == 400

def test_update_config_non_existent_service(client):
    response = client.post("/config/nonexistent_service/feature1", json={"value": "newValue"})
    assert response.status_code == 404

def test_update_config_non_existent_setting(client):
    response = client.post("/config/service1/nonexistent_setting", json={"value": "newValue"})
    assert response.status_code == 404
