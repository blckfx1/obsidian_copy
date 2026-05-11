import dearpygui.dearpygui as dpg
from pathlib import Path
from core.vault import Vault
from datetime import date


class MiniVaultWindow:
    def __init__(self, vault_path=None):
        self.vault = Vault(vault_path)
        self.current_note_path: Path = None
        self._build_ui()

        if not self.vault.is_valid():
            self._show_open_vault_dialog()

    def _build_ui(self):
        with dpg.window(tag="main_window", no_title_bar=False, no_close=True, no_collapse=True) as self.main_window:
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open Vault...", callback=self._open_vault)
                    dpg.add_menu_item(label="New Note", callback=self._new_note)
                    dpg.add_separator()
                    dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

            with dpg.group(horizontal=True):
                # Sidebar
                with dpg.child_window(width=300, tag="sidebar"):
                    dpg.add_text("Vault", bullet=True)
                    self.tree = dpg.add_tree_node(label="Root", tag="file_tree")
                    dpg.add_button(label="📅 Daily Note", callback=self._create_daily_note, width=-1)

                # Editor + Preview
                with dpg.child_window(width=-1):
                    with dpg.group(horizontal=True, horizontal_spacing=10):
                        # Editor
                        with dpg.child_window(width=-1, tag="editor_pane"):
                            dpg.add_text("Editor", bullet=True)
                            self.editor = dpg.add_input_text(
                                multiline=True,
                                width=-1,
                                height=-1,
                                callback=self._on_editor_change,
                                tag="editor_input"
                            )

                        # Live Preview
                        with dpg.child_window(width=-1, tag="preview_pane"):
                            dpg.add_text("Preview", bullet=True)
                            # FIXED: Use add_text with wrap instead of add_text_wrap
                            self.preview = dpg.add_text(
                                "",
                                tag="preview_text",
                                wrap=0,                    # 0 = wrap to window width
                            )

# -------------------------------------------------------
    def _show_open_vault_dialog(self):
        def callback(sender, app_data):
            try:
                # More safe path extraction for Cyrillic usernames
                folder = None
                if isinstance(app_data, dict):
                    folder = app_data.get('file_path_name') or app_data.get('current_path')
                
                print(f"✅ Selected raw: {folder}")

                if folder:
                    folder_str = str(folder)  # force string
                    print(f"✅ Using path: {folder_str}")
                    
                    self.vault.set_path(folder_str)
                    dpg.delete_item("open_vault_dialog")
                    self._refresh_file_tree()
                    print("✅ Vault opened successfully!")
                else:
                    print("⚠️ No folder received from dialog")
            except Exception as e:
                print(f"❌ ERROR in vault callback: {e}")
                import traceback
                traceback.print_exc()

        with dpg.file_dialog(
            directory_selector=True,
            show=True,
            tag="open_vault_dialog",
            callback=callback,
            width=900,
            height=700,
            default_path="C:\\Users"   # Start from Users folder to reduce Cyrillic issues
        ):
            pass
# ---------------------------------------------------------------

    def _open_vault(self, sender=None, app_data=None):
        self._show_open_vault_dialog()

# -------------------------------------------------------------

def _refresh_file_tree(self):
        if not self.vault.is_valid():
            print("❌ Vault not valid")
            return
        try:
            dpg.delete_item(self.tree, children_only=True)
            self._build_tree(self.vault.path, self.tree)
            print("✅ File tree refreshed")
        except Exception as e:
            print(f"❌ Tree error: {e}")

# --------------------------------------------------------------

    def _build_tree(self, directory: Path, parent):
        """Build file tree safely"""
        if not directory.exists() or not directory.is_dir():
            print(f"⚠️ Not a valid directory: {directory}")
            return

        try:
            items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.is_dir() and item.name not in ("__pycache__", ".git", "venv"):
                    # Create folder node
                    node = dpg.add_tree_node(
                        label=f"📁 {item.name}", 
                        parent=parent,
                        default_open=item.name in ("Daily Notes", "")  # open root
                    )
                    self._build_tree(item, node)   # recursive

                elif item.suffix.lower() == ".md":
                    # Add file
                    dpg.add_selectable(
                        label=f"📄 {item.name}",
                        parent=parent,
                        callback=lambda s, a, u=item: self._open_note(u)
                    )
        except Exception as e:
            print(f"❌ Error building tree in {directory}: {e}")

# --------------------------------------------------------------

    def _open_note(self, path: Path):
        self.current_note_path = path
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            dpg.set_value("editor_input", content)
            self._update_preview(content)
        except Exception as e:
            dpg.set_value("editor_input", f"Error opening file: {e}")

    def _new_note(self):
        if not self.vault.is_valid():
            return

        def create_note(sender, app_data):
            name = dpg.get_value("new_note_name").strip()
            if name:
                if not name.endswith(".md"):
                    name += ".md"
                path = self.vault.path / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"# {name[:-3]}\n\n", encoding="utf-8")
                self._open_note(path)
            dpg.delete_item("new_note_window")

        with dpg.window(label="New Note", modal=True, tag="new_note_window", width=350, height=120):
            dpg.add_text("Note name:")
            dpg.add_input_text(tag="new_note_name", hint="e.g. Project Ideas or Meeting Notes")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Create", callback=create_note, width=150)
                dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("new_note_window"), width=150)

    def _create_daily_note(self):
        if not self.vault.is_valid():
            return

        daily_dir = self.vault.path / "Daily Notes"
        daily_dir.mkdir(exist_ok=True)

        today = date.today().isoformat()
        path = daily_dir / f"{today}.md"

        if not path.exists():
            path.write_text(f"# Daily Note - {today}\n\n", encoding="utf-8")

        self._open_note(path)

    def _on_editor_change(self, sender, app_data):
        if self.current_note_path:
            content = dpg.get_value("editor_input")
            try:
                with open(self.current_note_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self._update_preview(content)
            except Exception:
                pass  # silently fail for now

    # ==================== UPDATED PREVIEW METHOD ====================
    def _update_preview(self, markdown_text: str):
        import markdown

        html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])

        # Convert common HTML to readable text for preview
        plain = (
            html
            .replace("<h1>", "# ")
            .replace("</h1>", "\n\n")

            .replace("<h2>", "## ")
            .replace("</h2>", "\n\n")

            .replace("<h3>", "### ")
            .replace("</h3>", "\n\n")
            .replace("<h4>", "#### ")
            .replace("</h4>", "\n\n")

            .replace("<p>", "")
            .replace("</p>", "\n\n")

            .replace("<strong>", "**")
            .replace("</strong>", "**")
            .replace("<em>", "*")
            .replace("</em>", "*")
            .replace("<code>", "`")
            .replace("</code>", "`")
            
            .replace("<ul>", "")
            .replace("</ul>", "\n")
            .replace("<li>", "• ")
            .replace("</li>", "\n")
        )

        # Remove any remaining HTML tags
        import re
        plain = re.sub(r'<[^>]+>', '', plain)

        dpg.set_value("preview_text", plain.strip())