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

    @bp.route("/config/<service_name>/<setting_name>/<property_name>", methods=["POST"])
    def update_config_property(service_name, setting_name, property_name):
        """
        Update a specific property of a configuration setting for a service
        """
        # if service name or setting name is not in cache
        if service_name not in config_manager.config_cache:
            abort(404, f"Config for service '{service_name}' not found")

        if setting_name not in config_manager.config_cache[service_name]:
            abort(
                404, f"Setting '{setting_name}' not found for service '{service_name}'"
            )

        # get the new value
        new_value = request.json.get("value")
        if not new_value:
            abort(400, "Missing value in request body")

        # check if property_name is valid
        if property_name not in ["value", "type", "enabled"]:
            abort(400, f"Invalid property name '{property_name}'")

        # Validate the new_value
        if not isinstance(new_value, str) or new_value.strip() == "":
            abort(400, "Invalid value. Expected a non-empty string")

        if len(new_value) > 1024:
            abort(400, f"Maximum length of value is 1024 characters")

        success = config_manager.update_config(
            service_name, setting_name, property_name, new_value
        )
        if success:
            return jsonify(
                {
                    "status": f"Updated '{property_name}' of '{setting_name}' for '{service_name}'"
                }
            )
        else:
            abort(
                404,
                f"Failed to update '{property_name}' of '{setting_name}' for '{service_name}'",
            )

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
