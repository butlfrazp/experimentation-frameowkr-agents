"""Test suite for module executable functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from exp_platform_cli.executables.module_executable import ModuleExecutable
from exp_platform_cli.models import DataModelRow, ModuleExecutableConfig


class TestModuleExecutable:
    """Test module executable functionality."""

    def create_test_module(self, tmp_path: Path, module_name: str, content: str) -> Path:
        """Helper to create a test module."""
        module_path = tmp_path / f"{module_name}.py"
        module_path.write_text(content)
        return module_path

    def test_load_module_from_current_directory(self, tmp_path: Path, monkeypatch):
        """Test loading module from current directory."""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)
        
        # Create a test module
        module_content = '''
def run(**kwargs) -> str:
    # Get input directly from kwargs (passed from data_input)
    input_value = kwargs.get('input', 'no_input')
    return f"processed: {input_value}"
'''
        self.create_test_module(tmp_path, "test_module", module_content)
        
        # Create test row and config
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test_input"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="test_module",
            processor="run"
        )
        
        # Test module loading
        executable = ModuleExecutable(row, config)
        result = executable.execute(**row.data_input)
        
        assert result.data_output == "processed: test_input"

    def test_load_module_with_py_extension(self, tmp_path: Path, monkeypatch):
        """Test that module loading works with .py extension in path."""
        monkeypatch.chdir(tmp_path)
        
        module_content = '''
def process(**kwargs) -> str:
    input_value = kwargs.get('input', 'no_input')
    return f"result: {input_value}"
'''
        self.create_test_module(tmp_path, "processor", module_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "data"},
            expected_output={"output": "expected"},
        )
        
        # Test with .py extension in path
        config = ModuleExecutableConfig(
            path="processor.py",
            processor="process"
        )
        
        executable = ModuleExecutable(row, config)
        result = executable.execute(**row.data_input)
        
        assert result.data_output == "result: data"

    def test_module_not_found_error(self, tmp_path: Path, monkeypatch):
        """Test error handling when module is not found."""
        monkeypatch.chdir(tmp_path)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="nonexistent_module",
            processor="run"
        )
        
        with pytest.raises(FileNotFoundError, match="Executable module not found"):
            ModuleExecutable(row, config)

    def test_processor_not_found_error(self, tmp_path: Path, monkeypatch):
        """Test error when processor function doesn't exist in module."""
        monkeypatch.chdir(tmp_path)
        
        module_content = '''
def other_function():
    return "not the processor"
'''
        self.create_test_module(tmp_path, "test_module", module_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="test_module",
            processor="missing_processor"
        )
        
        with pytest.raises(AttributeError, match="does not expose 'missing_processor'"):
            ModuleExecutable(row, config)

    def test_module_with_class_processor(self, tmp_path: Path, monkeypatch):
        """Test loading a processor that is a class with run method."""
        monkeypatch.chdir(tmp_path)
        
        module_content = '''
class Processor:
    def run(self, **kwargs) -> str:
        input_value = kwargs.get('input', 'no_input')
        return f"class processed: {input_value}"
'''
        self.create_test_module(tmp_path, "class_module", module_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test_data"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="class_module",
            processor="Processor"
        )
        
        executable = ModuleExecutable(row, config)
        result = executable.execute(**row.data_input)
        
        assert result.data_output == "class processed: test_data"

    def test_module_execution_with_kwargs(self, tmp_path: Path, monkeypatch):
        """Test module execution with additional kwargs."""
        monkeypatch.chdir(tmp_path)
        
        module_content = '''
def run(**kwargs) -> str:
    input_value = kwargs.get('input', 'no_input')
    context_value = kwargs.get('context')
    
    parts = [f"input: {input_value}"]
    if context_value:
        parts.append(f"context: {context_value}")
    return ", ".join(parts)
'''
        self.create_test_module(tmp_path, "kwargs_module", module_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={
                "input": "test_input",
                "context": "test_context"
            },
            expected_output={"output": "expected_result"},
        )
        
        config = ModuleExecutableConfig(
            path="kwargs_module",
            processor="run"
        )
        
        executable = ModuleExecutable(row, config)
        result = executable.execute(**row.data_input)
        
        expected_parts = ["input: test_input", "context: test_context"]
        for part in expected_parts:
            assert part in result.data_output

    def test_module_returns_datamodelrow(self, tmp_path: Path, monkeypatch):
        """Test module that returns a DataModelRow directly."""
        monkeypatch.chdir(tmp_path)
        
        module_content = '''
from exp_platform_cli.models import DataModelRow

def run(row: DataModelRow, **kwargs) -> DataModelRow:
    row.data_output = {"processed": True, "original": row.data_input}
    return row
'''
        self.create_test_module(tmp_path, "row_module", module_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test_data"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="row_module",
            processor="run"
        )
        
        executable = ModuleExecutable(row, config)
        result = executable.execute()
        
        assert result.data_output["processed"] is True
        assert result.data_output["original"] == {"input": "test_data"}

    def test_invalid_module_syntax(self, tmp_path: Path, monkeypatch):
        """Test handling of modules with syntax errors."""
        monkeypatch.chdir(tmp_path)
        
        # Create module with syntax error
        invalid_content = '''
def run(input: str, **kwargs) -> str:
    return f"processed: {input"  # Missing closing brace
'''
        self.create_test_module(tmp_path, "invalid_module", invalid_content)
        
        row = DataModelRow(
            id="test_row",
            data_input={"input": "test"},
            expected_output={"output": "expected"},
        )
        
        config = ModuleExecutableConfig(
            path="invalid_module",
            processor="run"
        )
        
        with pytest.raises(Exception):  # Could be SyntaxError or ImportError
            ModuleExecutable(row, config)