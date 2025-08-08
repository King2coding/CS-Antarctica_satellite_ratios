# Contributing to Antarctica Precipitation Correction

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the Antarctica GPCP precipitation correction package.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/antarctica-precipitation-correction.git
   cd antarctica-precipitation-correction
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular

### Testing
- Write tests for new functionality
- Ensure existing tests pass before submitting
- Use pytest for testing framework

### Documentation
- Update README.md if adding new features
- Add docstrings with proper parameter descriptions
- Include examples in docstrings where helpful

## Types of Contributions

### Bug Reports
- Use the GitHub issue tracker
- Include minimal reproducible example
- Specify your environment (OS, Python version, package versions)

### Feature Requests
- Open an issue to discuss before implementation
- Explain the use case and benefits
- Consider backward compatibility

### Code Contributions
1. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Commit with descriptive messages
6. Push to your fork and create a pull request

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Add or update tests as needed
3. Update documentation
4. Ensure all tests pass
5. Write a clear pull request description

## Scientific Accuracy

This project deals with scientific data and methods. Please ensure:
- Algorithms are scientifically sound
- Units are clearly documented
- Methods are properly referenced
- Validation against known results where possible

## Data Handling

- Respect data licensing and attribution requirements
- Document data sources clearly
- Handle missing data appropriately
- Consider memory efficiency for large datasets

## Questions?

Feel free to open an issue for questions about:
- Development setup
- Implementation details
- Scientific methodology
- Usage examples

Thank you for contributing to improving precipitation analysis over Antarctica! 🐧❄️
