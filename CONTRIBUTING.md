# Contributing to OneTask API

Thank you for considering contributing to OneTask API! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct, which requires all contributors to be respectful and inclusive.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the Issues section
- If not, create a new issue with a clear title and description
- Include steps to reproduce, expected vs. actual behavior, and any relevant information
- Add the "bug" label to the issue

### Suggesting Features

- Check if the feature has already been suggested in the Issues section
- If not, create a new issue with a clear title and description
- Explain why this feature would be useful to most users
- Add the "enhancement" label to the issue

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the code style guidelines
   - Write tests for your changes
   - Update documentation as needed
4. **Run tests locally**
   ```bash
   pytest
   ```
5. **Commit your changes**
   ```bash
   git commit -am "Add feature X" 
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Submit a Pull Request**
   - Clearly describe the problem and solution
   - Reference any related issues
   - Ensure all tests pass

## Development Environment Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/onetask-api.git
   cd onetask-api
   ```

2. Set up a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -e .
   ```
   This installs the project in development mode with all dependencies from pyproject.toml.

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run development server
   ```bash
   ./run_dev_server.sh
   ```

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single responsibility

## Testing Guidelines

- Write unit tests for all new features
- Ensure all tests pass before submitting pull requests
- Aim for at least 80% test coverage for new code

## Documentation Guidelines

- Update documentation for all user-facing changes
- Use clear, concise language
- Include examples where appropriate

## Database Migrations

- Use SQLAlchemy models for database changes
- Document any schema changes in your pull request

## Git Commit Guidelines

- Use clear, descriptive commit messages
- Reference issue numbers in commit messages when applicable
- Keep commits focused on a single change

## Additional Notes

- If you have questions at any point, feel free to ask in the Issues section
- For complex changes, consider discussing in an issue before implementing

Thank you for contributing to OneTask API!