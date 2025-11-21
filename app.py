from flask import Flask, render_template
import importlib
import os
import inspect
from config import Config
import traceback


app = Flask(__name__)

# Load configuration from the Config object
app.config.from_object(Config)
base_url = app.config['BASE_URL']


# Auto-register blueprints from /apps folder
def register_blueprints():
    apps_dir = os.path.join(os.path.dirname(__file__), 'apps')

    for folder in os.listdir(apps_dir):
        print(f"\n📂 Scanning app folder: {folder}")
        folder_path = os.path.join(apps_dir, folder)

        # Check if the folder has a 'routes' subfolder
        routes_path = os.path.join(folder_path, 'routes')
        if os.path.isdir(routes_path):
            for file in os.listdir(routes_path):
                # Only import .py files (not __init__.py or others)
                if file.endswith(".py") and not file.startswith("__"):
                    module_name = f"apps.{folder}.routes.{file[:-3]}"
                    route_name = file[:-3]  # remove the .py extension
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, 'bp'):
                            app.register_blueprint(module.bp, url_prefix=f"/{base_url}/{folder}/{route_name}")
                            print(f"✅ Registered blueprint: {folder}/{file} → /{route_name}")
                        else:
                            print(f"⚠️ No 'bp' found in {module_name}")
                    except Exception:
                        print(f"❌ Failed to import {module_name}:")
                        traceback.print_exc()


# 🧩 CALL IT HERE!
register_blueprints()


@app.route("/")
def index():
    routes_grouped = {}

    for rule in app.url_map.iter_rules():
        # Skip static and root route
        if rule.endpoint == "static" or rule.rule == "/":
            continue

        # Get description from docstring
        view_func = app.view_functions[rule.endpoint]
        doc = inspect.getdoc(view_func) or "No description"

        url = rule.rule

        # Determine topic from first segment
        topic = url.strip(f"{base_url}").split("/")[0] or None
        if not topic:
            continue  # skip root-level API if needed

        if topic not in routes_grouped:
            routes_grouped[topic] = []

        routes_grouped[topic].append({
            "endpoint": rule.endpoint.split(".")[-1],
            "url": url,
            "methods": ", ".join(rule.methods - {"HEAD", "OPTIONS"}),
            "description": doc
        })

    return render_template("dashboard.html", routes_grouped=routes_grouped)




# Prevent running this file directly
if __name__ == "__main__":
    raise RuntimeError("❌ Do NOT run app.py directly. Use: python starter.py")