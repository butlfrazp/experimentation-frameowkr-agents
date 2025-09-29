"""
Interactive Jupyter Widget Interface for the Experimentation Platform CLI.

This module provides a user-friendly widget-based interface for data scientists
to interact with the experimentation platform without needing to use command-line tools.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import ipywidgets as widgets
import yaml
from IPython.display import clear_output

# Import the CLI components directly
try:
    from exp_platform_cli.cli import (
        discover_config_files,
        load_and_validate_config,
        run_experiment_with_resilience,
    )
    from exp_platform_cli.models import ExperimentConfig
    from exp_platform_cli.services import ConfigLoader, DatasetService

    DIRECT_IMPORT = True
except ImportError:
    # Fallback to subprocess calls if imports fail
    DIRECT_IMPORT = False
    print("⚠️  Direct import failed, falling back to subprocess calls")


class ExperimentPlatformWidget:
    """Main widget interface for the Experimentation Platform."""

    def __init__(self):
        self.config_data = {}
        self.current_config_path = None
        self.experiment_results = []

        # Create all widgets
        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _create_widgets(self):
        """Create all the UI widgets."""

        # Header
        self.header = widgets.HTML(
            value="<h1>🧪 Experimentation Platform - Interactive Interface</h1>"
        )

        # Tab container
        self.tab = widgets.Tab()

        # Tab 1: Experiment Designer
        self.experiment_tab = self._create_experiment_designer()

        # Tab 2: Config Editor
        self.config_tab = self._create_config_editor()

        # Tab 3: Results Viewer
        self.results_tab = self._create_results_viewer()

        # Tab 4: Tutorial Runner
        self.tutorial_tab = self._create_tutorial_runner()

        # Set up tabs
        self.tab.children = [
            self.experiment_tab,
            self.config_tab,
            self.results_tab,
            self.tutorial_tab,
        ]
        self.tab.titles = [
            "🚀 Experiment Designer",
            "⚙️ Config Editor",
            "📊 Results",
            "📚 Tutorials",
        ]

        # Output area
        self.output = widgets.Output(layout=widgets.Layout(height="300px", overflow="scroll"))

    def _create_experiment_designer(self):
        """Create the experiment designer interface."""

        # Dataset section
        self.dataset_name = widgets.Text(
            description="Dataset Name:",
            placeholder="e.g., my_experiment",
            style={"description_width": "120px"},
        )

        self.dataset_version = widgets.Text(
            description="Version:", value="1.0", style={"description_width": "120px"}
        )

        # Module section
        self.module_path = widgets.Text(
            description="Module Path:",
            placeholder="e.g., my_module.py",
            style={"description_width": "120px"},
        )

        self.processor_name = widgets.Text(
            description="Processor:", value="run", style={"description_width": "120px"}
        )

        # Evaluators section
        self.evaluator_selector = widgets.SelectMultiple(
            options=[
                "conversation_quality",
                "response_relevance",
                "tool_call_accuracy",
                "equivalent",
            ],
            value=["conversation_quality"],
            description="Evaluators:",
            style={"description_width": "120px"},
        )

        # Output settings
        self.output_path = widgets.Text(
            description="Output Path:",
            value="data/experiments",
            style={"description_width": "120px"},
        )

        self.local_mode = widgets.Checkbox(
            description="Local Mode", value=True, style={"description_width": "120px"}
        )

        # Data input area
        self.data_input = widgets.Textarea(
            description="Input Data (JSON):",
            placeholder='[\\n  {"input": "Hello", "expected_output": "Hi there!"},\\n  {"input": "Goodbye", "expected_output": "See you later!"}\\n]',
            layout=widgets.Layout(width="100%", height="150px"),
            style={"description_width": "120px"},
        )

        # Buttons
        self.generate_config_btn = widgets.Button(
            description="Generate Config", button_style="primary", icon="cogs"
        )

        self.run_experiment_btn = widgets.Button(
            description="Run Experiment", button_style="success", icon="play"
        )

        # Layout
        form_items = [
            widgets.HBox([self.dataset_name, self.dataset_version]),
            widgets.HBox([self.module_path, self.processor_name]),
            self.evaluator_selector,
            widgets.HBox([self.output_path, self.local_mode]),
            self.data_input,
            widgets.HBox([self.generate_config_btn, self.run_experiment_btn]),
        ]

        return widgets.VBox(form_items)

    def _create_config_editor(self):
        """Create the configuration editor interface."""

        # File operations
        self.config_file_path = widgets.Text(
            description="Config File:",
            placeholder="path/to/config.yaml",
            style={"description_width": "100px"},
        )

        self.load_config_btn = widgets.Button(
            description="Load Config", button_style="info", icon="upload"
        )

        self.save_config_btn = widgets.Button(
            description="Save Config", button_style="warning", icon="save"
        )

        # Config editor
        self.config_editor = widgets.Textarea(
            description="Configuration:",
            layout=widgets.Layout(width="100%", height="400px"),
            style={"description_width": "100px"},
        )

        # Validation
        self.validate_btn = widgets.Button(
            description="Validate Config", button_style="primary", icon="check"
        )

        self.validation_output = widgets.HTML()

        # Layout
        controls = widgets.HBox(
            [self.config_file_path, self.load_config_btn, self.save_config_btn, self.validate_btn]
        )

        return widgets.VBox([controls, self.config_editor, self.validation_output])

    def _create_results_viewer(self):
        """Create the results viewer interface."""

        # Results directory browser
        self.results_dir = widgets.Text(
            description="Results Dir:",
            value="data/experiments",
            style={"description_width": "100px"},
        )

        self.refresh_results_btn = widgets.Button(
            description="Refresh", button_style="info", icon="refresh"
        )

        # Results list
        self.results_list = widgets.Select(
            description="Experiments:",
            layout=widgets.Layout(height="200px"),
            style={"description_width": "100px"},
        )

        # Results display
        self.results_display = widgets.Output(
            layout=widgets.Layout(height="300px", overflow="scroll")
        )

        # Controls
        controls = widgets.HBox([self.results_dir, self.refresh_results_btn])

        return widgets.VBox([controls, self.results_list, self.results_display])

    def _create_tutorial_runner(self):
        """Create the tutorial runner interface."""

        # Tutorial selector
        self.tutorial_selector = widgets.Dropdown(
            options=[
                ("📖 01: Quickstart (5 minutes)", "tutorials/01-quickstart"),
                ("🏗️ 04: Simple Experiment", "tutorials/04-simple-experiment"),
                ("📚 Basic Concepts", "tutorials/03-basic-concepts"),
            ],
            description="Tutorial:",
            style={"description_width": "100px"},
        )

        # Options
        self.install_deps = widgets.Checkbox(
            description="Install Dependencies", value=True, style={"description_width": "150px"}
        )

        # Run button
        self.run_tutorial_btn = widgets.Button(
            description="Run Tutorial", button_style="success", icon="graduation-cap"
        )

        # Tutorial info
        self.tutorial_info = widgets.HTML(value="<p>Select a tutorial to see more information.</p>")

        # Layout
        controls = widgets.HBox([self.tutorial_selector, self.install_deps, self.run_tutorial_btn])

        return widgets.VBox(
            [
                controls,
                self.tutorial_info,
            ]
        )

    def _setup_layout(self):
        """Set up the overall layout."""
        self.main_container = widgets.VBox(
            [
                self.header,
                self.tab,
                widgets.HTML("<hr>"),
                widgets.HTML("<h3>📋 Execution Log</h3>"),
                self.output,
            ]
        )

    def _bind_events(self):
        """Bind event handlers to widgets."""

        # Experiment Designer
        self.generate_config_btn.on_click(self._on_generate_config)
        self.run_experiment_btn.on_click(self._on_run_experiment)

        # Config Editor
        self.load_config_btn.on_click(self._on_load_config)
        self.save_config_btn.on_click(self._on_save_config)
        self.validate_btn.on_click(self._on_validate_config)

        # Results Viewer
        self.refresh_results_btn.on_click(self._on_refresh_results)
        self.results_list.observe(self._on_result_selected, names="value")

        # Tutorial Runner
        self.run_tutorial_btn.on_click(self._on_run_tutorial)
        self.tutorial_selector.observe(self._on_tutorial_selected, names="value")

    def _on_generate_config(self, button):
        """Generate configuration from form inputs."""
        with self.output:
            clear_output(wait=True)
            print("🔧 Generating configuration...")

            try:
                # Parse input data
                if self.data_input.value.strip():
                    try:
                        input_data = json.loads(self.data_input.value)
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON in input data: {e}")
                        return
                else:
                    input_data = []

                # Build config
                config = {
                    "dataset": {
                        "name": self.dataset_name.value or "experiment",
                        "version": self.dataset_version.value or "1.0",
                        "config": {"expected_output_field": "expected_output"},
                    },
                    "executable": {
                        "type": "module",
                        "path": self.module_path.value or "my_module",
                        "processor": self.processor_name.value or "run",
                        "config": {},
                    },
                    "evaluation": [
                        {"id": f"{eval_name}_eval", "name": eval_name, "data_mapping": {}}
                        for eval_name in self.evaluator_selector.value
                    ],
                    "local_mode": self.local_mode.value,
                    "output_path": self.output_path.value or "data/experiments",
                }

                # Update config editor
                yaml_config = yaml.dump(config, default_flow_style=False, indent=2)
                self.config_editor.value = yaml_config

                # Create dataset if data provided
                if input_data:
                    self._create_dataset(
                        config["dataset"]["name"], config["dataset"]["version"], input_data
                    )

                print("✅ Configuration generated successfully!")
                print("📝 Config updated in editor tab")
                if input_data:
                    print(f"📊 Dataset created with {len(input_data)} samples")

            except Exception as e:
                print(f"❌ Error generating config: {e}")

    def _create_dataset(self, name: str, version: str, data: list[dict]):
        """Create a dataset from input data."""
        dataset_dir = Path("data/datasets") / name / version
        dataset_dir.mkdir(parents=True, exist_ok=True)

        dataset_file = dataset_dir / "data.jsonl"
        with dataset_file.open("w") as f:
            for item in data:
                f.write(json.dumps(item) + "\\n")

    def _on_run_experiment(self, button):
        """Run the experiment."""
        with self.output:
            clear_output(wait=True)
            print("🚀 Running experiment...")

            try:
                if not self.config_editor.value.strip():
                    print("❌ No configuration available. Generate config first.")
                    return

                # Save config to temporary file
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                    f.write(self.config_editor.value)
                    config_path = f.name

                try:
                    if DIRECT_IMPORT:
                        # Use direct function call
                        result = run_experiment_with_resilience(Path(config_path))
                        print("✅ Experiment completed successfully!")
                    else:
                        # Use subprocess
                        result = subprocess.run(
                            ["exp-cli", "run", config_path], capture_output=True, text=True, cwd="."
                        )

                        if result.returncode == 0:
                            print("✅ Experiment completed successfully!")
                            print(result.stdout)
                        else:
                            print(f"❌ Experiment failed: {result.stderr}")

                finally:
                    # Clean up temp file
                    Path(config_path).unlink(missing_ok=True)

            except Exception as e:
                print(f"❌ Error running experiment: {e}")

    def _on_load_config(self, button):
        """Load configuration from file."""
        with self.output:
            clear_output(wait=True)
            print(f"📁 Loading config from {self.config_file_path.value}...")

            try:
                config_path = Path(self.config_file_path.value)
                if not config_path.exists():
                    print(f"❌ File not found: {config_path}")
                    return

                with config_path.open() as f:
                    if config_path.suffix.lower() in [".yaml", ".yml"]:
                        content = f.read()
                    else:  # JSON
                        data = json.load(f)
                        content = yaml.dump(data, default_flow_style=False, indent=2)

                self.config_editor.value = content
                self.current_config_path = config_path
                print("✅ Configuration loaded successfully!")

            except Exception as e:
                print(f"❌ Error loading config: {e}")

    def _on_save_config(self, button):
        """Save configuration to file."""
        with self.output:
            clear_output(wait=True)

            if not self.config_file_path.value.strip():
                print("❌ Please specify a file path")
                return

            try:
                config_path = Path(self.config_file_path.value)
                config_path.parent.mkdir(parents=True, exist_ok=True)

                with config_path.open("w") as f:
                    f.write(self.config_editor.value)

                print(f"✅ Configuration saved to {config_path}")

            except Exception as e:
                print(f"❌ Error saving config: {e}")

    def _on_validate_config(self, button):
        """Validate the current configuration."""
        with self.output:
            clear_output(wait=True)
            print("🔍 Validating configuration...")

            try:
                if not self.config_editor.value.strip():
                    print("❌ No configuration to validate")
                    return

                # Parse YAML
                config_data = yaml.safe_load(self.config_editor.value)

                # Basic validation
                required_fields = ["dataset", "executable"]
                missing_fields = [field for field in required_fields if field not in config_data]

                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    self.validation_output.value = (
                        f"<div style='color: red;'>❌ Missing: {', '.join(missing_fields)}</div>"
                    )
                    return

                # More detailed validation if direct import available
                if DIRECT_IMPORT:
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                        f.write(self.config_editor.value)
                        temp_path = f.name

                    try:
                        config = load_and_validate_config(Path(temp_path))
                        print("✅ Configuration is valid!")
                        self.validation_output.value = (
                            "<div style='color: green;'>✅ Configuration is valid!</div>"
                        )
                    except Exception as e:
                        print(f"❌ Validation error: {e}")
                        self.validation_output.value = f"<div style='color: red;'>❌ {str(e)}</div>"
                    finally:
                        Path(temp_path).unlink(missing_ok=True)
                else:
                    print("✅ Basic validation passed!")
                    self.validation_output.value = (
                        "<div style='color: green;'>✅ Basic validation passed!</div>"
                    )

            except yaml.YAMLError as e:
                print(f"❌ YAML parsing error: {e}")
                self.validation_output.value = (
                    f"<div style='color: red;'>❌ YAML Error: {str(e)}</div>"
                )
            except Exception as e:
                print(f"❌ Validation error: {e}")
                self.validation_output.value = f"<div style='color: red;'>❌ Error: {str(e)}</div>"

    def _on_refresh_results(self, button):
        """Refresh the results list."""
        with self.output:
            clear_output(wait=True)
            print("🔄 Refreshing results...")

            try:
                results_dir = Path(self.results_dir.value)
                if not results_dir.exists():
                    print(f"❌ Results directory not found: {results_dir}")
                    self.results_list.options = []
                    return

                # Find experiment directories
                experiments = []
                for path in results_dir.rglob("exp*/"):
                    if path.is_dir():
                        # Get relative path for display
                        rel_path = path.relative_to(results_dir)
                        experiments.append((str(rel_path), str(path)))

                experiments.sort(key=lambda x: x[1], reverse=True)  # Most recent first
                self.results_list.options = experiments

                print(f"✅ Found {len(experiments)} experiments")

            except Exception as e:
                print(f"❌ Error refreshing results: {e}")

    def _on_result_selected(self, change):
        """Handle result selection."""
        if not change["new"]:
            return

        experiment_path = Path(change["new"])

        with self.results_display:
            clear_output(wait=True)

            try:
                print(f"📊 Experiment: {experiment_path.name}")
                print("=" * 50)

                # Load config if available
                config_files = list(experiment_path.glob("config.*"))
                if config_files:
                    config_file = config_files[0]
                    print(f"\\n⚙️ Configuration ({config_file.name}):")
                    if config_file.suffix.lower() in [".yaml", ".yml"]:
                        with config_file.open() as f:
                            config_content = f.read()
                        print(
                            config_content[:500] + "..."
                            if len(config_content) > 500
                            else config_content
                        )

                # Load results if available
                results_file = experiment_path / "local_metrics_summary.json"
                if results_file.exists():
                    with results_file.open() as f:
                        results = json.load(f)

                    print("\\n📈 Results Summary:")
                    for evaluator, metrics in results.items():
                        print(f"  {evaluator}:")
                        for metric, value in metrics.items():
                            if isinstance(value, float):
                                print(f"    {metric}: {value:.4f}")
                            else:
                                print(f"    {metric}: {value}")

                # Load execution data
                data_file = experiment_path / "data.jsonl"
                if data_file.exists():
                    print("\\n📋 Execution Data:")
                    with data_file.open() as f:
                        lines = f.readlines()
                    print(f"  Total rows: {len(lines)}")

                    # Show first few results
                    for i, line in enumerate(lines[:3]):
                        try:
                            row_data = json.loads(line)
                            print(f"  Row {i+1}: {row_data.get('id', 'unknown')}")
                            if "data_output" in row_data:
                                output = str(row_data["data_output"])
                                print(
                                    f"    Output: {output[:100]}..."
                                    if len(output) > 100
                                    else f"    Output: {output}"
                                )
                        except Exception:
                            pass

                    if len(lines) > 3:
                        print(f"    ... and {len(lines) - 3} more rows")

            except Exception as e:
                print(f"❌ Error loading results: {e}")

    def _on_run_tutorial(self, button):
        """Run the selected tutorial."""
        with self.output:
            clear_output(wait=True)
            tutorial_path = self.tutorial_selector.value
            print(f"🎓 Running tutorial: {tutorial_path}")

            try:
                cmd = ["exp-cli", "run-directory", tutorial_path]
                if self.install_deps.value:
                    cmd.append("--install-deps")

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

                if result.returncode == 0:
                    print("✅ Tutorial completed successfully!")
                    print("\\n📋 Output:")
                    print(result.stdout)
                else:
                    print("❌ Tutorial failed:")
                    print(result.stderr)

            except Exception as e:
                print(f"❌ Error running tutorial: {e}")

    def _on_tutorial_selected(self, change):
        """Update tutorial information when selection changes."""
        tutorial_info = {
            "tutorials/01-quickstart": """
            <div style='padding: 10px; background-color: #f0f8ff; border-left: 4px solid #007acc;'>
            <h4>📖 Quickstart Tutorial (5 minutes)</h4>
            <p><strong>What you'll learn:</strong></p>
            <ul>
                <li>How to install and verify the platform</li>
                <li>Run your first conversation quality experiment</li>
                <li>View and understand results</li>
            </ul>
            <p><strong>Prerequisites:</strong> None - perfect for beginners!</p>
            </div>
            """,
            "tutorials/04-simple-experiment": """
            <div style='padding: 10px; background-color: #f0fff0; border-left: 4px solid #28a745;'>
            <h4>🏗️ Simple Experiment Tutorial</h4>
            <p><strong>What you'll learn:</strong></p>
            <ul>
                <li>Build experiments from scratch</li>
                <li>Create custom text summarization modules</li>
                <li>Use multiple evaluators (relevance + quality)</li>
                <li>Understand configuration patterns</li>
            </ul>
            <p><strong>Prerequisites:</strong> Basic Python knowledge</p>
            </div>
            """,
            "tutorials/03-basic-concepts": """
            <div style='padding: 10px; background-color: #fff8f0; border-left: 4px solid #fd7e14;'>
            <h4>📚 Basic Concepts Guide</h4>
            <p><strong>What you'll learn:</strong></p>
            <ul>
                <li>Platform architecture and components</li>
                <li>Dataset, execution, and evaluation concepts</li>
                <li>Configuration file structure</li>
                <li>Best practices and workflows</li>
            </ul>
            <p><strong>Prerequisites:</strong> Completed quickstart tutorial</p>
            </div>
            """,
        }

        selected = change["new"]
        self.tutorial_info.value = tutorial_info.get(
            selected, "<p>Select a tutorial to see more information.</p>"
        )

    def display(self):
        """Display the main widget interface."""
        return self.main_container


def create_experiment_interface():
    """Create and return the experiment interface widget."""
    interface = ExperimentPlatformWidget()

    # Add some helpful initial content
    interface.config_editor.value = """# Sample Configuration
dataset:
  name: my_experiment
  version: "1.0"
  config:
    expected_output_field: expected_output

executable:
  type: module
  path: my_module
  processor: run
  config: {}

evaluation:
  - id: quality_eval
    name: conversation_quality
    data_mapping: {}

local_mode: true
output_path: data/experiments
"""

    return interface


# Helper functions for notebook usage
def quick_experiment(
    module_path: str,
    data: list[dict[str, Any]],
    evaluators: list[str] = None,
    dataset_name: str = "quick_experiment",
    output_path: str = "data/experiments",
) -> str:
    """
    Run a quick experiment with minimal setup.

    Args:
        module_path: Path to the Python module containing the 'run' function
        data: List of input data dictionaries
        evaluators: List of evaluator names to use
        dataset_name: Name for the dataset
        output_path: Where to store results

    Returns:
        Path to the experiment results
    """
    if evaluators is None:
        evaluators = ["conversation_quality"]

    # Create config
    config = {
        "dataset": {
            "name": dataset_name,
            "version": "1.0",
            "config": {"expected_output_field": "expected_output"},
        },
        "executable": {"type": "module", "path": module_path, "processor": "run", "config": {}},
        "evaluation": [
            {"id": f"{name}_eval", "name": name, "data_mapping": {}} for name in evaluators
        ],
        "local_mode": True,
        "output_path": output_path,
    }

    # Create dataset
    dataset_dir = Path("data/datasets") / dataset_name / "1.0"
    dataset_dir.mkdir(parents=True, exist_ok=True)

    dataset_file = dataset_dir / "data.jsonl"
    with dataset_file.open("w") as f:
        for item in data:
            f.write(json.dumps(item) + "\\n")

    # Create and run config
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
        config_path = f.name

    try:
        if DIRECT_IMPORT:
            result = run_experiment_with_resilience(Path(config_path))
            print("✅ Experiment completed successfully!")
        else:
            result = subprocess.run(["exp-cli", "run", config_path], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Experiment completed successfully!")
                print(result.stdout)
            else:
                print(f"❌ Experiment failed: {result.stderr}")

    finally:
        Path(config_path).unlink(missing_ok=True)

    # Return path to results (this would need to be extracted from the actual run)
    return f"{output_path}/{dataset_name}/1.0/"


def load_results(experiment_path: str) -> dict[str, Any]:
    """
    Load experiment results for analysis.

    Args:
        experiment_path: Path to the experiment directory

    Returns:
        Dictionary containing results, config, and metadata
    """
    exp_path = Path(experiment_path)
    results = {}

    # Load metrics
    metrics_file = exp_path / "local_metrics_summary.json"
    if metrics_file.exists():
        with metrics_file.open() as f:
            results["metrics"] = json.load(f)

    # Load config
    config_files = list(exp_path.glob("config.*"))
    if config_files:
        config_file = config_files[0]
        with config_file.open() as f:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                results["config"] = yaml.safe_load(f)
            else:
                results["config"] = json.load(f)

    # Load execution data
    data_file = exp_path / "data.jsonl"
    if data_file.exists():
        results["rows"] = []
        with data_file.open() as f:
            for line in f:
                if line.strip():
                    results["rows"].append(json.loads(line))

    return results
