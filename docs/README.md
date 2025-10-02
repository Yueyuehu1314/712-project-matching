# ProjectMatching - Student-Project Intelligent Matching System

A knowledge graph-based intelligent system for matching students with suitable projects based on their skills, interests, and academic background.

## 🎯 Features

- **Document Processing**: Convert project proposals (DOCX, PDF, PPT) to structured Markdown
- **Knowledge Graph Generation**: Build comprehensive knowledge graphs for projects, students, and courses
- **Intelligent Matching**: Match students with projects based on skill requirements and interests
- **Profile Generation**: Generate student profiles using Ollama LLM
- **Similarity Analysis**: Calculate and analyze student-project similarity matrices

## 📁 Project Structure

```
ProjectMatching/
├── src/                    # Source code
│   ├── converters/         # Document converters
│   ├── knowledge_graphs/   # KG generators
│   ├── profile/           # Student profile generators
│   ├── matching/          # Matching algorithms
│   ├── utils/             # Utility functions
│   └── cli/               # Command-line interfaces
├── data/                  # Data files
│   ├── raw/               # Original files
│   └── processed/         # Processed files
├── outputs/               # Generated outputs
├── docs/                  # Documentation
├── tests/                 # Test files
└── scripts/               # Helper scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Ollama (for profile generation)
- Required Python packages (see requirements.txt)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ProjectMatching.git
cd ProjectMatching

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-kg.txt
```

### Usage

#### 1. Convert Documents

```bash
python src/converters/document_converter.py
```

#### 2. Generate Knowledge Graphs

```bash
# Generate project knowledge graphs
python src/cli/kg_cli.py build --project-dir data/processed/projects_md

# Generate balanced knowledge graphs (recommended)
python src/knowledge_graphs/balanced_kg_generator.py
```

#### 3. Generate Student Profiles

```bash
# Generate profiles using Ollama
python src/cli/main_cli.py generate --all

# Chat with a generated student
python src/cli/main_cli.py chat --project "path/to/project.md"
```

#### 4. Calculate Similarity

```bash
python src/matching/similarity_matrix.py
```

## 📊 Data Flow

```
Project Files (.docx, .pdf) 
    ↓ 
Document Converter 
    ↓
Markdown Files 
    ↓
Knowledge Graph Generator 
    ↓
Knowledge Graphs (JSON, PNG) 
    ↓
Matching Algorithm 
    ↓
Similarity Matrix & Recommendations
```

## 🔧 Configuration

Edit `config/default.yaml` to customize:
- Model selection (for LLM)
- Output directories
- Matching parameters
- Visualization settings

## 📖 Documentation

- [Usage Guide](USAGE.md) - Detailed usage instructions
- [API Documentation](API.md) - API reference
- [中文使用指南](USAGE_CN.md) - Chinese user guide
- [项目总结](PROJECT_SUMMARY_CN.md) - Chinese project summary

## 🧪 Testing

```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Lynn - Initial work

## 🙏 Acknowledgments

- QUT Faculty for course data
- Ollama for local LLM support
- NetworkX for graph processing

