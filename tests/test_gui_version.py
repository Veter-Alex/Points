import importlib.util
import os
import sys


def test_app_version_in_gui():
    # Проверяем, что APP_VERSION определён и используется в заголовке окна
    gui_path = os.path.join(os.path.dirname(__file__), '../src/gui_manager.py')
    spec = importlib.util.spec_from_file_location("gui_manager", gui_path)
    gui = importlib.util.module_from_spec(spec)
    sys.modules["gui_manager"] = gui
    spec.loader.exec_module(gui)
    assert hasattr(gui, "APP_VERSION")
    assert gui.APP_VERSION.startswith("v")
    # Проверка, что PointsGUI использует APP_VERSION в title
    # (Проверяем наличие строки в исходном коде)
    with open(gui_path, encoding="utf-8") as f:
        code = f.read()
        assert f"PointsManager {gui.APP_VERSION}" in code
        assert f"PointsManager {gui.APP_VERSION}" in code
