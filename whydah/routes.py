from flask import Blueprint, jsonify, abort, request
from .errors import AppError


def config_bp(config_manager):
    bp = Blueprint("config_bp", __name__)

    @bp.route("/config/<service_name>", methods=["GET"])
    def get_config(service_name):
        """
        Get the configuration for a service
        """
        config = config_manager.get_config(service_name)
        if not config:
            abort(404, f"Config for service '{service_name}' not found")
        return jsonify(config)

    @bp.route("/config/<service_name>/<setting_name>", methods=["POST"])
    def update_config(service_name, setting_name):
        """
        Update a configuration setting for a service
        """
        new_value = request.json.get("value")
        if new_value is None:
            abort(400, "Missing 'value' in the request body")

        # Validate the new_value
        if not isinstance(new_value, str) or new_value.strip() == "":
            abort(400, "Invalid value. Expected a non-empty string")

        if len(new_value) > 1024:
            abort(400, f"Maximum length of value is 1024 characters")

        success = config_manager.update_config(service_name, setting_name, new_value)
        if success:
            return jsonify({"status": f"Updated '{setting_name}' for '{service_name}'"})
        else:
            abort(404, f"Failed to update '{setting_name}' for '{service_name}'")


    @bp.route("/config/refresh", methods=["POST"])
    def refresh_configs():
        """
        Refresh the configuration cache
        """
        success = config_manager.refresh_configs()
        if success:
            return jsonify({"status": "Configurations refreshed"})
        else:
            raise AppError("Failed to refresh configurations")

    @bp.route("/config", methods=["GET"])
    def get_all_configs():
        """
        Get all the configurations
        """
        services = list(config_manager.config_cache.keys())
        return jsonify(services)

    return bp
