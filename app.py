from flask import Flask, render_template
import importlib
import os
import inspect

app = Flask(__name__)

# Auto-register blueprints from /apps folder
def register_blueprints():
    apps_dir = os.path.join(os.path.dirname(__file__), 'apps')
    for folder in os.listdir(apps_dir):
        folder_path = os.path.join(apps_dir, folder)
        if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, 'routes.py')):
            module_name = f"apps.{folder}.routes"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'bp'):
                    app.register_blueprint(module.bp, url_prefix=f"/{folder}")
                    print(f"✅ Registered blueprint: {folder}")
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
