import dearpygui.dearpygui as dpg
import os
from pathlib import Path
from ui.main_window import MiniVaultWindow
from utils.config import load_config, save_config

def main():
    dpg.create_context()
    dpg.create_viewport(title="MiniVault", width=1400, height=900, min_width=800, min_height=600)

    # Load last vault or prompt for one
    config = load_config()
    vault_path = config.get("vault_path")

    if not vault_path or not os.path.exists(vault_path):
        vault_path = None

    app = MiniVaultWindow(vault_path=vault_path)

    with dpg.font_registry():
        default_font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 18)  # Adjust path if needed
        dpg.bind_font(default_font)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(app.main_window, True)
    dpg.start_dearpygui()

    # Save config on close
    save_config({"vault_path": app.vault_path})
    dpg.destroy_context()


if __name__ == "__main__":
    main()