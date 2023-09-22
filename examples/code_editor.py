"""
Code editor example.

Run with:

    python code_editor.py PATH
"""

import os
import pathlib
import sys
from pathlib import Path
from typing import Optional

from rich.syntax import Syntax

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.reactive import Reactive
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, TextArea
from textual.widgets.text_area import BUILTIN_LANGUAGES


class CodeEditor(App):
    """CodeBrowser with TextArea Super Powers."""

    CSS_PATH = "code_editor.tcss"
    BINDINGS = [
        Binding(key="ctrl+q", action="quit", description="Quit"),
        Binding(key="ctrl+t", action="toggle_files", description="Toggle Tree"),
        Binding(key="ctrl+s", action="save", description="Save"),
    ]

    show_tree: Reactive[bool] = var(True)
    """Whether to show the directory tree."""

    def __init__(self, path: str):
        """Initialize our app and create widget instance attributes."""
        super().__init__()
        self.file_path: pathlib.Path = Path(path)
        self.sub_title: str = str(self.file_path)
        self.text_area: TextArea = TextArea(id="code")
        self.text_area.display = False
        self.selected_file: Optional[Path] = None
        self.file_content: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()
        with Container():
            yield DirectoryTree(self.file_path, id="tree-view")
            with VerticalScroll(id="code-view"):
                yield self.text_area
        yield Footer()

    def on_mount(self) -> None:
        """Focus on the directory tree when the app is mounted."""
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        event.stop()
        self.selected_file = event.path
        self.sub_title = str(self.selected_file)
        try:
            self.file_content = self.selected_file.read_text()
            self.text_area.display = True
        except Exception:
            self.sub_title = "ERROR"
            self.text_area.display = False
            self.text_area.language = None
            self.notify(
                message=f"{self.selected_file.name} could not be loaded",
                title="File Error",
                severity="error",
            )
            self.selected_file = None
        else:
            self.load_text_area(text=self.file_content, file_path=self.selected_file)

    def load_text_area(self, text: str, file_path: pathlib.Path) -> None:
        """Load text into the text area - try to guess the language."""
        lexer = Syntax.guess_lexer(str(file_path), code=text)
        self.text_area.load_text(self.file_content)
        if lexer in BUILTIN_LANGUAGES:
            self.text_area.language = lexer
        else:
            self.text_area.language = None

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    def action_save(self) -> None:
        """Save the current file if it has been modified."""
        if self.selected_file:
            if self.text_area.text != self.file_content:
                self.selected_file.write_text(self.text_area.text)
                self.file_content = self.text_area.text
                self.notify(message=str(self.selected_file), title="File Saved")

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")


args = sys.argv
if len(args) > 1:
    path = args[1]
else:
    path = os.getcwd()

app = CodeEditor(path=path)

if __name__ == "__main__":
    app.run()
