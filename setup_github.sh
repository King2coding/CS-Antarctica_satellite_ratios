#!/bin/bash

# GitHub Repository Setup Script for CS-Antarctica GPCP Precipitation Correction
# This script initializes a Git repository and sets up for GitHub

echo "🚀 Setting up CS-Antarctica GPCP Precipitation Correction GitHub Repository"
echo "=========================================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if already has commits
if git log --oneline -1 >/dev/null 2>&1; then
    echo "📝 Repository already initialized with commits."
    echo "📄 Adding any new files to Git..."
    git add .
    
    # Check if there are changes to commit
    if ! git diff --cached --quiet; then
        echo "💾 Creating new commit with updates..."
        git commit -m "Update: CS-Antarctica GPCP correction package

- Consolidated repository in original working directory
- Updated documentation and examples
- Improved plotting with corner-positioned month titles
- Ready for GitHub publication"
    else
        echo "✅ No new changes to commit."
    fi
else
    # Initialize git repository
    echo "📁 Initializing Git repository..."
    git init

    # Add all files
    echo "📄 Adding files to Git..."
    git add .

    # Create initial commit
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: CS-Antarctica GPCP precipitation correction

- Complete Python package structure with main working script
- Direct and Reza's correction methods
- Visualization tools with improved axis readability
- Example scripts and advanced analysis
- Documentation and setup files"
fi

echo ""
echo "✅ Local Git repository ready!"
echo ""
echo "🔗 Next steps to create GitHub repository:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: CS-Antarctica_satellite_ratios"
echo "   OR: cs-antarctica-gpcp-ratios (shorter alternative)"
echo "3. Do NOT initialize with README, .gitignore, or license (we already have these)"
echo "4. Copy the repository URL (e.g., https://github.com/yourusername/CS-Antarctica_satellite_ratios.git)"
echo "5. Run the following commands:"
echo ""
echo "   git remote add origin https://github.com/yourusername/CS-Antarctica_satellite_ratios.git"
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
