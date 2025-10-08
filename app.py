from flask import Flask, render_template
import importlib
import os
import inspect

app = Flask(__name__)

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
                            app.register_blueprint(module.bp, url_prefix=f"/{folder}/{route_name}")
                            print(f"✅ Registered blueprint: {folder}/{file} → /{route_name}")
                        else:
                            print(f"⚠️ No 'bp' found in {module_name}")
                    except Exception as e:
                        print(f"❌ Failed to import {module_name}: {e}")


# 🧩 CALL IT HERE!
register_blueprints()


@app.route("/")
def index():
    # Introspect all routes for display
    routes_info = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            view_func = app.view_functions[rule.endpoint]
            doc = inspect.getdoc(view_func) or "No description"
            routes_info.append({
                "endpoint": rule.endpoint,
                "url": str(rule),
                "methods": ', '.join(rule.methods - {"HEAD", "OPTIONS"}),
                "description": doc
            })
    return render_template("dashboard.html", routes=routes_info)


if __name__ == "__main__":
    app.run(debug=True)
