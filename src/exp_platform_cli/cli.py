"""Command-line interface for the experimentation platform CLI."""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path
from typing import Optional

import click

from .logger import get_logger
from .orchestrator import Orchestrator
from .services.config_loader import ConfigLoader
from .services.dataset_service import DatasetService
from .utils import ensure_directories

logger = get_logger()


class ExperimentError(Exception):
    """Base exception for experiment execution errors."""
    pass


class ConfigurationError(ExperimentError):
    """Raised when configuration is invalid."""
    pass


class DatasetError(ExperimentError):
    """Raised when dataset operations fail."""
    pass


class ExecutionError(ExperimentError):
    """Raised when experiment execution fails."""
    pass


def validate_config_file(config_path: Path) -> None:
    """Validate configuration file exists and is readable."""
    if not config_path.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    if not config_path.is_file():
        raise ConfigurationError(f"Configuration path is not a file: {config_path}")
    
    if not config_path.suffix.lower() in ['.yaml', '.yml', '.json']:
        logger.warning(f"Configuration file has unexpected extension: {config_path.suffix}")
    
    try:
        config_path.read_text(encoding='utf-8')
    except Exception as e:
        raise ConfigurationError(f"Cannot read configuration file {config_path}: {e}")


def validate_dataset_root(dataset_root: Optional[Path]) -> Optional[Path]:
    """Validate and resolve dataset root directory."""
    if dataset_root is None:
        return None
    
    resolved_path = dataset_root.expanduser().resolve()
    
    if not resolved_path.exists():
        logger.warning(f"Dataset root does not exist, will be created: {resolved_path}")
        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created dataset root directory: {resolved_path}")
        except Exception as e:
            raise DatasetError(f"Cannot create dataset root directory {resolved_path}: {e}")
    
    if not resolved_path.is_dir():
        raise DatasetError(f"Dataset root is not a directory: {resolved_path}")
    
    return resolved_path


def setup_experiment_environment() -> None:
    """Setup required directories and environment for experiment execution."""
    try:
        ensure_directories()
        logger.debug("Experiment environment setup completed")
    except Exception as e:
        logger.error(f"Failed to setup experiment environment: {e}")
        raise ExecutionError(f"Environment setup failed: {e}")


def load_and_validate_config(config_path: Path) -> object:
    """Load and validate experiment configuration with retries."""
    max_retries = 3
    retry_delay = 1.0
    
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.debug(f"Loading configuration (attempt {attempt + 1}/{max_retries})")
            config = ConfigLoader.load_config(config_path)
            logger.info(f"Configuration loaded successfully: {config.describe()}")
            return config
        except Exception as e:
            last_error = e
            logger.warning(f"Configuration load attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    raise ConfigurationError(f"Failed to load configuration after {max_retries} attempts: {last_error}")


def run_experiment_with_resilience(
    config_path: Path,
    dataset_root: Optional[Path] = None,
    dry_run: bool = False,
    max_retries: int = 1
) -> str:
    """Execute experiment with comprehensive error handling and retries."""
    
    # Setup and validation
    setup_experiment_environment()
    validate_config_file(config_path)
    dataset_root = validate_dataset_root(dataset_root)
    
    # Load configuration
    config = load_and_validate_config(config_path)
    
    if dry_run:
        logger.info(
            "✅ Dry run validation complete for dataset [bold]%s:%s[/]",
            config.dataset.name,
            config.dataset.version,
        )
        logger.info("Dry run mode - no experiment execution performed")
        return "dry-run"
    
    # Create services with error handling
    try:
        logger.debug("Initializing dataset service")
        dataset_service = DatasetService(dataset_root)
        logger.debug("Dataset service initialized successfully")
    except Exception as e:
        raise DatasetError(f"Failed to initialize dataset service: {e}")
    
    # Execute experiment with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"🚀 Starting experiment execution (attempt {attempt + 1}/{max_retries})")
            
            orchestrator = Orchestrator(dataset_service=dataset_service)
            experiment_id = orchestrator.run(str(config_path))
            
            logger.success(f"🎉 Experiment completed successfully: {experiment_id}")
            logger.info(f"Experiment metadata: dataset={config.dataset.name}:{config.dataset.version}")
            
            return experiment_id
            
        except KeyboardInterrupt:
            logger.warning("⚠️  Experiment interrupted by user")
            raise
            
        except Exception as e:
            last_error = e
            logger.error(f"💥 Experiment execution failed (attempt {attempt + 1}): {e}")
            logger.debug(f"Full error details: {traceback.format_exc()}")
            
            if attempt < max_retries - 1:
                retry_delay = 2.0 * (2 ** attempt)  # Exponential backoff
                logger.info(f"🔄 Retrying experiment in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ All {max_retries} execution attempts failed")
    
    raise ExecutionError(f"Experiment execution failed after {max_retries} attempts: {last_error}")


@click.group(invoke_without_command=True)
@click.option('--verbose', '-v', count=True, help='Increase verbosity (use -v, -vv, or -vvv)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-error output')
@click.pass_context
def cli(ctx: click.Context, verbose: int, quiet: bool):
    """🧪 Experimentation Platform CLI
    
    A robust platform for running and evaluating experiments with support for:
    • Local and cloud evaluation modes
    • Platform-native and foundry-style evaluators  
    • Configurable output paths and data mapping
    • Comprehensive error handling and resilience
    """
    
    # Configure logging based on verbosity
    import logging
    if quiet:
        logger._logger.setLevel(logging.WARNING)
    elif verbose >= 3:
        logger._logger.setLevel(logging.DEBUG)
    elif verbose >= 2:
        logger._logger.setLevel(logging.INFO)
    elif verbose >= 1:
        logger._logger.setLevel(logging.INFO)
    
    # If no command specified, run the default run command
    if ctx.invoked_subcommand is None:
        ctx.invoke(run, ctx.params.get('config'))


@cli.command()
@click.argument('config', type=click.Path(exists=True, path_type=Path))
@click.option('--dataset-root', '-d', type=click.Path(path_type=Path), 
              help='Override dataset root directory')
@click.option('--dry-run', is_flag=True, help='Validate configuration without executing experiment')
@click.option('--max-retries', '-r', default=1, type=click.IntRange(1, 10),
              help='Maximum number of execution retry attempts (1-10)')
@click.option('--output-path', '-o', type=click.Path(path_type=Path),
              help='Override output path for experiment results')
def run(config: Path, dataset_root: Optional[Path], dry_run: bool, max_retries: int, output_path: Optional[Path]):
    """🚀 Run an experiment from configuration file.
    
    CONFIG: Path to experiment configuration file (YAML or JSON)
    
    Examples:
      exp-cli run experiment.yaml
      exp-cli run experiment.yaml --dry-run
      exp-cli run experiment.yaml -d /custom/datasets -r 3
    """
    
    try:
        logger.banner("Experiment Execution")
        logger.info(f"📋 Configuration: [bold]{config.absolute()}[/]")
        
        if dataset_root:
            logger.info(f"📁 Dataset root: [bold]{dataset_root.absolute()}[/]")
        
        if output_path:
            logger.info(f"💾 Output path: [bold]{output_path.absolute()}[/]")
            # TODO: Integrate output_path override with configuration
        
        if dry_run:
            logger.info("🔍 Running in dry-run mode")
        
        if max_retries > 1:
            logger.info(f"🔄 Max retries configured: {max_retries}")
        
        start_time = time.time()
        
        experiment_id = run_experiment_with_resilience(
            config_path=config,
            dataset_root=dataset_root,
            dry_run=dry_run,
            max_retries=max_retries
        )
        
        execution_time = time.time() - start_time
        logger.success(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        
        if not dry_run:
            logger.info(f"🔗 Experiment ID: [bold]{experiment_id}[/]")
        
    except KeyboardInterrupt:
        logger.warning("🛑 Execution interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
        
    except (ConfigurationError, DatasetError, ExecutionError) as e:
        logger.error(f"❌ {e.__class__.__name__}: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


@cli.command()
@click.argument('config', type=click.Path(exists=True, path_type=Path))
def validate(config: Path):
    """✅ Validate experiment configuration without execution.
    
    CONFIG: Path to experiment configuration file
    """
    
    try:
        logger.banner("Configuration Validation")
        logger.info(f"📋 Validating: [bold]{config.absolute()}[/]")
        
        # File validation
        validate_config_file(config)
        logger.success("✅ Configuration file is valid and readable")
        
        # Configuration loading validation
        experiment_config = load_and_validate_config(config)
        logger.success("✅ Configuration syntax and structure are valid")
        
        logger.info(f"📊 Experiment details: {experiment_config.describe()}")
        logger.info(f"🏃 Execution mode: {'Local' if experiment_config.local_mode else 'Cloud'}")
        logger.info(f"📈 Evaluators configured: {len(experiment_config.evaluators)}")
        
        for i, evaluator in enumerate(experiment_config.evaluators, 1):
            logger.info(f"   {i}. {evaluator.name} (id: {evaluator.id})")
        
        logger.success("🎉 Configuration validation completed successfully")
        
    except (ConfigurationError, DatasetError) as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 Unexpected validation error: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


@cli.command('run-directory')
@click.argument('directory', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--install-deps', is_flag=True, help='Install dependencies from requirements.txt in directory')
@click.option('--module-path', '-m', help='Python module path to execute (e.g., "examples.basic_math")')
@click.option('--config-pattern', '-p', default='*.yaml', help='Pattern to match configuration files')
@click.option('--dry-run', is_flag=True, help='Validate configurations without executing experiments')
@click.option('--max-retries', '-r', default=1, type=click.IntRange(1, 10),
              help='Maximum number of execution retry attempts (1-10)')
def run_directory(directory: Path, install_deps: bool, module_path: Optional[str], 
                 config_pattern: str, dry_run: bool, max_retries: int):
    """🚀 Run experiments from a directory with automatic dependency management.
    
    DIRECTORY: Path to directory containing experiment configurations and code
    
    This command will:
    • Install dependencies from requirements.txt if --install-deps is specified
    • Discover all configuration files matching the pattern
    • Execute experiments with proper module path resolution
    • Provide comprehensive progress reporting
    
    Examples:
      exp-cli run-directory ./experiments --install-deps
      exp-cli run-directory ./tutorials/basic --module-path tutorials.basic -p "experiment_*.yaml"
    """
    
    try:
        logger.banner("Directory-Based Experiment Execution")
        logger.info(f"📁 Target directory: [bold]{directory.absolute()}[/]")
        
        # Install dependencies if requested
        if install_deps:
            install_directory_dependencies(directory)
        
        # Add directory to Python path for module resolution
        if module_path:
            setup_module_path(directory, module_path)
        
        # Discover configuration files
        config_files = discover_config_files(directory, config_pattern)
        logger.info(f"📋 Found {len(config_files)} configuration files")
        
        if not config_files:
            logger.warning("No configuration files found matching pattern")
            return
        
        # Execute each configuration
        results = []
        for i, config_file in enumerate(config_files, 1):
            logger.info(f"🔄 Processing configuration {i}/{len(config_files)}: {config_file.name}")
            
            try:
                experiment_id = run_experiment_with_resilience(
                    config_path=config_file,
                    dataset_root=directory / "datasets" if (directory / "datasets").exists() else None,
                    dry_run=dry_run,
                    max_retries=max_retries
                )
                results.append({'config': config_file.name, 'experiment_id': experiment_id, 'status': 'success'})
                
            except Exception as e:
                logger.error(f"Failed to execute {config_file.name}: {e}")
                results.append({'config': config_file.name, 'experiment_id': None, 'status': 'failed', 'error': str(e)})
        
        # Summary report
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        logger.banner("Execution Summary")
        logger.info(f"📊 Total configurations: {len(results)}")
        logger.info(f"✅ Successful: {successful}")
        logger.info(f"❌ Failed: {failed}")
        
        if successful > 0:
            logger.info("🎉 Successful experiments:")
            for result in results:
                if result['status'] == 'success':
                    logger.info(f"   • {result['config']} → {result['experiment_id']}")
        
        if failed > 0:
            logger.warning("⚠️  Failed experiments:")
            for result in results:
                if result['status'] == 'failed':
                    logger.warning(f"   • {result['config']}: {result.get('error', 'Unknown error')}")
        
        logger.success(f"🏁 Directory execution completed: {successful}/{len(results)} successful")
        
    except Exception as e:
        logger.error(f"💥 Directory execution failed: {e}")
        sys.exit(1)


@cli.command()
def info():
    """ℹ️  Display platform information and available evaluators."""
    
    try:
        logger.banner("Platform Information")
        
        # Platform info
        from . import __version__
        logger.info(f"🏷️  Version: [bold]{__version__}[/]")
        
        # Available evaluators
        from .evaluators import enhanced_registry
        available_evaluators = list(enhanced_registry.available())
        logger.info(f"🔧 Available evaluators: {len(available_evaluators)}")
        
        for evaluator in sorted(set(available_evaluators)):  # Remove duplicates
            logger.info(f"   • {evaluator}")
        
        # Environment info
        import os
        artifact_root = os.getenv("EXP_CLI_ARTIFACT_ROOT", str(Path.cwd() / "data" / "experiments"))
        logger.info(f"📁 Artifact root: {artifact_root}")
        
        dataset_root = os.getenv("EXP_CLI_DATASET_ROOT", str(Path.cwd() / "data" / "datasets"))
        logger.info(f"📂 Dataset root: {dataset_root}")
        
        # Cloud configuration
        foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "Not configured")
        logger.info(f"☁️  Foundry endpoint: {foundry_endpoint}")
        
        logger.success("ℹ️  Platform information displayed")
        
    except Exception as e:
        logger.error(f"💥 Failed to retrieve platform information: {e}")
        sys.exit(1)


def install_directory_dependencies(directory: Path) -> None:
    """Install dependencies from requirements.txt in the specified directory."""
    requirements_file = directory / "requirements.txt"
    
    if not requirements_file.exists():
        logger.info("📦 No requirements.txt found, skipping dependency installation")
        return
    
    logger.info(f"📦 Installing dependencies from {requirements_file}")
    
    try:
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            cwd=directory
        )
        
        if result.returncode == 0:
            logger.success("✅ Dependencies installed successfully")
        else:
            logger.error(f"❌ Failed to install dependencies: {result.stderr}")
            raise RuntimeError(f"Dependency installation failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"💥 Error installing dependencies: {e}")
        raise


def setup_module_path(directory: Path, module_path: str) -> None:
    """Add directory to Python path and validate module path."""
    logger.info(f"🐍 Setting up module path: {module_path}")
    
    # Add directory to Python path
    import sys
    if str(directory.absolute()) not in sys.path:
        sys.path.insert(0, str(directory.absolute()))
        logger.debug(f"Added {directory.absolute()} to Python path")
    
    # Validate module can be imported
    try:
        import importlib
        importlib.import_module(module_path)
        logger.success(f"✅ Module {module_path} is importable")
    except ImportError as e:
        logger.warning(f"⚠️  Module {module_path} cannot be imported: {e}")
        logger.info("💡 Module will be resolved at execution time")


def discover_config_files(directory: Path, pattern: str) -> list[Path]:
    """Discover configuration files in directory matching the pattern."""
    logger.info(f"🔍 Searching for configuration files with pattern: {pattern}")
    
    import glob
    config_files = []
    
    # Search in directory and subdirectories
    for pattern_variant in [pattern, f"**/{pattern}"]:
        matches = list(directory.glob(pattern_variant))
        config_files.extend(matches)
    
    # Remove duplicates and sort
    config_files = sorted(set(config_files))
    
    # Filter to only include files (not directories)
    config_files = [f for f in config_files if f.is_file()]
    
    logger.debug(f"Found configuration files: {[f.name for f in config_files]}")
    return config_files


def app_main() -> None:
    """Entry-point used by uv script mapping."""
    cli()

