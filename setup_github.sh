#!/bin/bash

# GitHub Repository Setup Script for Antarctica Precipitation Correction
# This script initializes a Git repository and sets up for GitHub

echo "🚀 Setting up Antarctica Precipitation Correction GitHub Repository"
echo "=================================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository
echo "📁 Initializing Git repository..."
git init

# Add all files
echo "📄 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Antarctica GPCP precipitation correction package

- Complete Python package structure
- Direct and Reza's correction methods
- Visualization tools with improved axis readability
- Example scripts and advanced analysis
- Documentation and setup files"

echo ""
echo "✅ Local Git repository initialized successfully!"
echo ""
echo "🔗 Next steps to create GitHub repository:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: antarctica-precipitation-correction"
echo "3. Do NOT initialize with README, .gitignore, or license (we already have these)"
echo "4. Copy the repository URL (e.g., https://github.com/yourusername/antarctica-precipitation-correction.git)"
echo "5. Run the following commands:"
echo ""
echo "   git remote add origin https://github.com/yourusername/antarctica-precipitation-correction.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📊 Repository structure:"
echo "├── src/antarctica_precip_correction/    # Main package"
echo "├── examples/                            # Usage examples"
echo "├── original_script.py                   # Your original working script"
echo "├── README.md                            # Documentation"
echo "├── requirements.txt                     # Dependencies"
echo "├── setup.py                             # Package installation"
echo "├── LICENSE                              # MIT License"
echo "└── .gitignore                           # Git ignore rules"
echo ""
echo "🎯 Features included:"
echo "• Complete Python package for correction ratio computation"
echo "• Both direct division and Reza's smoothing methods"
echo "• Improved plotting with corner-positioned month titles"
echo "• Example scripts for basic and advanced usage"
echo "• Proper documentation and setup for easy installation"
echo "• Ready for PyPI publishing if desired"
echo ""
echo "Happy coding! 🐧❄️"
