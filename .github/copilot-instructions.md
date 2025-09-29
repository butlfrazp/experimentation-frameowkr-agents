<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created. — File created and confirmed present.

- [x] Clarify Project Requirements — Requirements captured: Python experimentation CLI with uv, linting, src layout, dev container.
	<!-- Ask for project type, language, and frameworks if not specified. Skip if already provided. -->

- [x] Scaffold the Project — Created uv-based Python CLI scaffolding with src/tests, devcontainer, and tooling files.
	<!--
	Ensure that the previous step has been marked as completed.
	Call project setup tool with projectType parameter.
	Run scaffolding command to create project files and folders.
	Use '.' as the working directory.
	If no appropriate projectType is available, search documentation using available tools.
	Otherwise, create the project structure manually using available file creation tools.
	-->

- [x] Customize the Project — Implemented Typer-based CLI, tests, lint config, and README guidance.
	<!--
	Verify that all previous steps have been completed successfully and you have marked the step as completed.
	Develop a plan to modify codebase according to user requirements.
	Apply modifications using appropriate tools and user-provided references.
	Skip this step for "Hello World" projects.
	-->

- [x] Install Required Extensions — No additional extensions specified; step skipped.
	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->

- [x] Compile the Project — Package installed successfully, CLI working, tutorials created and tested.
	<!--
	Verify that all previous steps have been completed.
	Install any missing dependencies.
	Run diagnostics and resolve any issues.
	Check for markdown files in project folder for relevant instructions on how to do this.
	-->

- [x] Create and Run Task — No build tasks needed for this Python CLI project; step skipped.
	<!--
	Verify that all previous steps have been completed.
	Check https://code.visualstudio.com/docs/debugtest/tasks to determine if the project needs a task. If so, use the create_and_run_task to create and launch a task based on package.json, README.md, and project structure.
	Skip this step otherwise.
	 -->

- [x] Launch the Project — CLI launches successfully; tutorials demonstrate full functionality.
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [x] Ensure Documentation is Complete — README and tutorials complete, copilot-instructions.md cleaned up.
	<!--
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->

## 🚀 Quick Start

The Experimentation Platform CLI is now ready! To get started:

```bash
# Install the platform
pip install -e .

# Run the quickstart tutorial
cd tutorials/01-quickstart
exp-cli run-directory . --install-deps
```

## 📚 Features

- **Agent Evaluation**: Comprehensive evaluation system for AI agents and tool calls
- **Foundry Integration**: Support for both platform-native and foundry-style evaluators
- **Directory Execution**: Run multiple experiments with automatic dependency management
- **Cloud Evaluation**: Support for cloud-based evaluation workflows
- **Rich CLI**: Click-based interface with comprehensive error handling and progress tracking
- **Tutorials**: Step-by-step guides from quickstart to advanced usage

## 🎯 Development Guidelines

- Work through each checklist item systematically  
- Keep communication concise and focused
- Follow development best practices
- Use the comprehensive tutorial system for learning and examples
