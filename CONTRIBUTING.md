# Contributing to Wibblo <!-- omit in toc -->

Thank you for your interest in contributing to Wibblo! This document provides guidelines and information for contributors.

- [Managing the Project](#managing-the-project)
- [Preparing the Environment Locally](#preparing-the-environment-locally)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Running the Game](#running-the-game)
- [Developing](#developing)
  - [Writing Code](#writing-code)
  - [Checking Code Quality](#checking-code-quality)
  - [Committing Code](#committing-code)
  - [Pushing Code to the Repositories](#pushing-code-to-the-repositories)
  - [Creating Pull Requests](#creating-pull-requests)
  - [Getting AI Assistance](#getting-ai-assistance)
  - [Delegating Tasks to AI Software Engineers](#delegating-tasks-to-ai-software-engineers)
- [Designing](#designing)
  - [Assets Acquisition](#assets-acquisition)
- [Managing Content](#managing-content)
- [Streamlining Operations](#streamlining-operations)
  - [Creating Standalone Executables](#creating-standalone-executables)
  - [Releasing](#releasing)
- [Marketing](#marketing)
- [Getting Help](#getting-help)
  - [Getting Asynchronous Help](#getting-asynchronous-help)
  - [Getting Real-Time Help](#getting-real-time-help)
- [License](#license)

## Managing the Project

> [!NOTE]
> You can edit the project management documents directly in the `./project` folder via GitHub website, but it's recommended to edit the documents locally.

We approach the project management in a git-based way. We foster an intuitive, transparent and proactivity-driven process. You can find all the project management documents in the `./project` folder.

Here's a brief overview of the documents:

- **[Plan](/project/PLAN.md)**: A plan for the project.
- **[Project Overview](/project/OVERVIEW.md)**: A summary of Wibblo's mission, vision, and progress.
- **[Roadmap](/project/ROADMAP.md)**: Key milestones and planned features to guide development.
- **[Backlog](/project/BACKLOG.md)**: A collection of tasks and ideas pending implementation.
- **[Todo](/project/TODO.md)**: The current tasks we’re working on.
- **[Suggestions](/project/SUGGESTIONS.md)**: Concepts and ideas under review for potential inclusion.
- **[Changelog](/project/CHANGELOG.md)**: A detailed chronological record of updates, changes, and improvements.

## Preparing the Environment Locally

You will need to have installed an IDE. It's recommended to use [Vscode](https://code.visualstudio.com/download) or any Vscode compatible editor.

1. **Install the main dependencies**
   - Ensure you have the following prerequisites installed on your system:
      - [Git](https://git-scm.com/downloads)
      - [Python 3.13+](https://www.python.org/downloads/)

2. **Configure the IDE (recommended)**
  - For Visual Studio Code, consider installing the following extensions:
    - [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)
    - [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) (optional)
    - [Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) (optional if you are using Cursor or another AI code assistant)
    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)
    - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
    - [Mypy](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker)
    - [Black](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
    - [Flake8](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)

3. **Clone the repository**

   Clone the repository to your local machine:

   ```sh
   git clone https://github.com/luisfuturist/challenge-pgz.git
   cd challenge-pgz/
   ```

4. **Create the virtual environment**

   Create the virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install the dependencies**

   Make sure to install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Submitting a Pull Request

1. **Create a branch**:
   ```bash
   git checkout -b feat/your-feature-name # or fix/your-fix-name, chore/your-chore-name, docs/your-docs-name, etc.
   ```

2. **Make your changes** following the guidelines

3. **Test your changes** by running the game. See [Running the Game](#running-the-game) for more information.

4. **Check code quality**:
   ```bash
   # Format code
   black .
   
   # Sort imports
   isort .
   
   # Run linter
   flake8 .
   
   # Run type checker
   mypy .
   ```

   See [Checking Code Quality](#checking-code-quality) for more information.

5. **Commit your changes**. See [Committing Code](#committing-code) for more information.

6. **Push and create a pull request**. See [Creating Pull Requests](#creating-pull-requests) for more information.

## Running the Game

To run the game, you can use the following command:

```bash
pgzrun src/main.py
```

## Developing

### Writing Code

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for public functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Checking Code Quality

For keeping the code organized, we use the following tools:

- [isort](https://pycqa.github.io/isort/): Used to sort the imports. It's automatically run when you save the files. You can also run it manually with `isort .`.
- [Black](https://black.readthedocs.io/en/stable/): Used to help us with the code formatting. It automatically fix the linting issues when you save the files. You can also run it manually with `black .`.
- [Flake8](https://flake8.pycqa.org/en/latest/): Used to lint the code. You can also run it manually with `flake8 .` to check the issues.
- [Mypy](https://mypy.readthedocs.io/en/stable/): Used to help us with the type safety. It's automatically run before the release. You can also run it manually with `mypy .`. // TODO: Add mypy to the CI/CD pipeline

### Committing Code

1. **Generate a commit message**
   - Use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format, in particular the [Angular Commit Convention](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit).
   - It's recommended to generate a commit message using AI of the IDE you are using. For example, in VSCode, you can use the `Copilot` extension to generate a commit message.
   - Check for warnings of already included authors in the commit message.

2. **Commit**
   - Run `git commit` to commit your changes or use the IDE's commit button.

### Pushing Code to the Repositories

You can use the following command to push your changes to the repository:

```bash
git push --set-upstream origin main # or `git push` if you have already set up upstream
```

### Creating Pull Requests

- Provide a clear description of the changes
- Include any relevant issue numbers
- Ensure all tests pass and code quality checks are satisfied
- Update documentation if necessary

### Getting AI Assistance

We can use AI code tools to get assistance for generating code, refactoring, debugging, testing, and documentation.

Examples: [Copilot](https://copilot.github.com/) (IDE extension), [Cursor](https://www.cursor.com/) (IDE fork), [Gemini CLI](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/) (terminal tool)

### Delegating Tasks to AI Software Engineers

We can use AI software engineers to delegate tasks across the project to an autonomous agent in the cloud. These tools can handle complex, multi-step tasks and integrate with your workflow.

Examples: [Devin](https://devin.ai/), [Codex](https://openai.com/codex/)

## Designing

Our design process is generally intuitive, but we can use different tools to design the application. We also search for inspirations in different sources, such as [Dribbble](https://dribbble.com/), [Behance](https://www.behance.net/) and/or [Pinterest](https://www.pinterest.com/). Also, we can be inspired by existing projects.

### Assets Acquisition

You can use the following resources to acquire assets for the game:

- [Kenney.nl Assets](https://kenney.nl/assets)
- [OpenGameArt.org](https://opengameart.org/)
- [GameDev Market](https://www.gamedevmarket.net/)

## Managing Content

// TODO: Add managing content section

## Streamlining Operations

// TODO: Add streamlining operations section

### Creating Standalone Executables

```bash
bash devops/scripts/build.sh
```

### Releasing

// TODO: Add releasing section

## Marketing

// TODO: Add marketing section

## Getting Help

> [!NOTE]
> For human-human communication, please prioritize asynchronous communication over real-time communication when possible.

### Getting Asynchronous Help

If you have questions or need help, we recommend you to follow these steps in order:

1. Read through this contributing guide.
2. Check the existing documentation in the `docs/` folder.
3. Refer to the official documentation for any relevant technologies.
4. Examine existing code, issues, and discussions for similar problems.
5. If you still need help, open a new issue for bugs or feature requests, or use a discussion for general questions.

### Getting Real-Time Help

For immediate assistance, we encourage you to use both community support and AI.

* **Community**: We have a [Discord server](https://discord.gg/RsYaUn3zQa) where you can get real-time help from our community members and core team if they are available.
* **AI Assistants:** We encourage you to leverage general-purpose AI Assistant, such as [Gemini](https://gemini.google.com/) or [ChatGPT](https://chatgpt.com/). They provide high-level, conversational help, such as explaining complex concepts, brainstorming solutions, and more.

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Wibblo! 🎮 
