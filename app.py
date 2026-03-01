from flask import Flask, Blueprint, render_template
import importlib
import importlib.util
import inspect
import os
import re
import traceback
from config import Config


app = Flask(__name__)

# Load configuration from the Config object
app.config.from_object(Config)
base_url = app.config["BASE_URL"]


def _safe_module_token(value):
    return re.sub(r"[^0-9a-zA-Z_]", "_", value)


def _load_module_from_path(folder_name, route_file_name, module_path):
    folder_token = _safe_module_token(folder_name)
    route_token = _safe_module_token(route_file_name)
    module_key = f"dynamic_routes.{folder_token}.{route_token}"

    spec = importlib.util.spec_from_file_location(module_key, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot build module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _extract_blueprint(module):
    module_bp = getattr(module, "bp", None)
    if isinstance(module_bp, Blueprint):
        return module_bp

    for module_value in vars(module).values():
        if isinstance(module_value, Blueprint):
            return module_value

    return None


# Auto-register blueprints from /apps folder
def register_blueprints():
    apps_dir = os.path.join(os.path.dirname(__file__), "apps")

    for folder in sorted(os.listdir(apps_dir)):
        folder_path = os.path.join(apps_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        # Check if the folder has a 'routes' subfolder
        routes_path = os.path.join(folder_path, "routes")
        if os.path.isdir(routes_path):
            print(f"\nScanning app folder: {folder}")

            for file in sorted(os.listdir(routes_path)):
                # Only import .py files (not __init__.py or others)
                if file.endswith(".py") and not file.startswith("__"):
                    module_name = f"apps.{folder}.routes.{file[:-3]}"
                    route_name = file[:-3]  # remove the .py extension
                    route_path = os.path.join(routes_path, file)
                    try:
                        try:
                            module = importlib.import_module(module_name)
                        except Exception:
                            module = _load_module_from_path(folder, route_name, route_path)

                        blueprint = _extract_blueprint(module)
                        if blueprint is None:
                            print(f"No Blueprint instance found in {folder}/{file}")
                            continue

                        app.register_blueprint(
                            blueprint, url_prefix=f"/{base_url}/{folder}/{route_name}"
                        )
                        print(f"Registered blueprint: {folder}/{file}")
                    except Exception:
                        print(f"Failed to import {module_name}:")
                        traceback.print_exc()


register_blueprints()


@app.route("/")
def index():
    routes_grouped = {}
    api_prefix = f"/{base_url}/"

    for rule in sorted(app.url_map.iter_rules(), key=lambda route_rule: route_rule.rule):
        # Skip static and root route
        if rule.endpoint == "static" or rule.rule == "/":
            continue

        if not rule.rule.startswith(api_prefix):
            continue

        # Get description from docstring
        view_func = app.view_functions[rule.endpoint]
        doc = inspect.getdoc(view_func) or "No description"

        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
        if not methods:
            continue

        route_path = rule.rule[len(api_prefix):]
        if not route_path:
            continue

        # Determine topic from first segment
        topic = route_path.split("/")[0] or None
        if not topic:
            continue  # skip root-level API if needed

        if topic not in routes_grouped:
            routes_grouped[topic] = []

        routes_grouped[topic].append(
            {
                "endpoint": rule.endpoint.split(".")[-1],
                "url": rule.rule,
                "methods": methods,
                "description": doc,
            }
        )

    return render_template("dashboard.html", routes_grouped=routes_grouped)


# Prevent running this file directly
if __name__ == "__main__":
    raise RuntimeError("Do NOT run app.py directly. Use: python starter.py")
