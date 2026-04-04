# ⚡ AI Code Reviewer

Docstring quality cockpit for Python workspaces — AI-powered analysis, fixing, style conversion, and automated test generation in a single Streamlit dashboard.

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit 1.42.0](https://img.shields.io/badge/Streamlit-1.42.0-red)
![Groq LLM](https://img.shields.io/badge/LLM-Groq-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Status: Active](https://img.shields.io/badge/Status-Active-success)

---

## Overview

AI Code Reviewer is a production-grade Streamlit application that brings intelligent docstring analysis, AI-powered fixing, and automated test generation to Python developers. Upload your codebase and instantly get comprehensive coverage reports, validation across three quality standards (PEP 257, darglint, AST parsing), AI-driven docstring improvements, flexible style conversion, and AI-generated unit tests — all with a modern IDE-like dashboard.

Whether you're reviewing legacy code, enforcing team standards, or scaling documentation quality across hundreds of files, this tool gives you visibility and automation that scales with your workspace.

---

## Features

### 🔍 Analysis & Coverage
- **Instant AST-based parsing** — Extract all functions, methods, classes, and their docstrings from Python files and zip archives
- **Function-level coverage metrics** — See exact docstring presence and completeness per function with visual breakdown
- **Workspace-wide metrics** — Dashboard shows total functions, coverage %, undocumented count, and style distribution
- **Multi-file batch analysis** — Process entire project folders with a single upload

### 🤖 AI-Powered Fixes
- **Model selection** — Choose from Llama 4 Scout (default), Compound Mini, Llama 3.3 70B, Kimi K2, GPT-OSS 120B, or GPT-OSS 20B for different performance/speed tradeoffs

### ✅ Validation (Three-Layer)
- **Faster fix mode** — Validation can skip follow-up test regeneration after fixes for quicker turnaround; enable the slower option only when you want fresh tests immediately

### 🧪 Testing
- **Automated pytest generation** — AI generates full unit test suites for functions with mocks, edge cases, and assertions
- **Smart caching** — Tests are cached per function; regenerate only when code changes
- **Health snapshot baseline** — First test generation creates a baseline for stability tracking
- **Test code inspection** — View generated test source code before using in CI/CD
- **Fast iteration** — Subsequent test runs use cache (< 5 seconds), not regenerated

### 📊 Dashboard & Reporting
- **Advanced filtering** — Filter by file, function, style, docstring status, test count, and custom ranges
- **Interactive search** — Find functions by name across all files in real-time
- **CSV/JSON export** — Export metrics, function lists, and test references for reports
- **Responsive tables** — Sortable columns, pagination, and inline code viewing
- **Visual metrics** — Pie charts, bar graphs, and trend data for coverage and style distribution

### 🎨 Style Management
- **Automatic style detection** — Detects Google, NumPy, reST, or mixed docstring formats in your codebase
- **Style conversion** — Convert between docstring formats (Google ↔ NumPy ↔ reST) with AI assistance
- **Batch conversion** — Normalize all docstrings in a file to a single style
- **Style statistics** — See style breakdown across workspace and per-file

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | Streamlit 1.42.0 |
| **LLM Provider** | Groq (multiple model support) |
| **Code Analysis** | Python AST, pydocstyle, darglint |
| **Testing** | pytest, pytest-json-report |
| **Visualization** | Plotly Express, pandas |
| **Environment** | python-dotenv, Python 3.9+ |
| **Runtime** | Windows/macOS/Linux compatible |

---

## Project Structure

```
AI_Powered_CRQA/
├── app.py                              # Streamlit entry point & main UI orchestration
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (create manually)
├── LICENSE                             # MIT License
├── README.md                           # This file
├── KNOWLEDGE_BASE.md                   # Complete feature & screen documentation
├── .streamlit/
│   └── config.toml                     # Streamlit configuration
├── .gitignore                          # Git ignore rules
│
├── core/                               # Business logic & analysis modules
│   ├── __init__.py                     # Package exports
│   ├── parser.py                       # AST-based function extraction & validation
│   ├── fix_code_with_ai.py             # Groq LLM docstring fixing & test caching
│   ├── convert_docstring_style.py      # Docstring style detection & conversion
│   └── generate_workspace_tests.py     # Automated pytest generation
│
├── faq/                                # Floating FAQ component
│   ├── __init__.py                     # Package exports
│   ├── faq_component.py                # FAQ popup UI & state management
│   └── faq_data.py                     # Static FAQ content per screen
│
├── tests/                              # Workspace test files
│   ├── __init__.py                     # Package marker
│   ├── test_darglint.py                # darglint validation tests
│   └── test_pydoc.py                   # pydocstyle validation tests
│
├── Test/                               # Original health snapshot test suite
│   ├── test_coverage_reporter.py       # Coverage metrics tests
│   ├── test_dashboard.py               # Dashboard rendering tests
│   ├── test_generator.py               # Test generation logic tests
│   ├── test_llm_integration.py         # Groq LLM integration tests
│   ├── test_parser.py                  # AST parser tests
│   └── test_validation.py              # Validation layer tests
│
├── workspace_tests/                    # Generated test artifacts
│   ├── fixed/                          # Copied and import-normalized test suite
│   │   ├── test_coverage_reporter.py
│   │   ├── test_dashboard.py
│   │   ├── test_generator.py
│   │   ├── test_llm_integration.py
│   │   ├── test_parser.py
│   │   └── test_validation.py
│   └── dynamic/                        # AI-generated project test suites
│       └── test_sample_a_google.py     # Example generated test file
│
├── examples/                           # Sample Python files for testing
│   ├── sample_a.py
│   ├── sample_b.py
│   ├── sample_c.py
│   ├── sample_d.py
│   ├── sample_e.py
│   ├── sample_f.py
│   ├── sample_g.py
│   ├── sample_h.py
│   └── sample_i.py
│
├── workspace_context/                  # Runtime workspace directory
│
└── venv/                               # Python virtual environment (created during setup)
```

---

## Getting Started

### Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **A Groq API key** — [Get one free at groq.com](https://console.groq.com)
- **Internet connection** (for LLM features; file upload/parsing works offline)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/lalith-thexplorer/AI-Powered-Code-Reviewer-and-Quality-Assistant.git
cd AI_Powered_CRQA
```

#### 2. Create and Activate a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Windows PowerShell
New-Item .env -ItemType File

# macOS/Linux
touch .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

**Required Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key for LLM docstring fixing, style conversion, and test generation | `gsk_aZbmP2HEC...` |

Obtain your key free from [Groq Console](https://console.groq.com).

#### 5. Run the Application

```bash
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

---

## How to Use

### 1. Upload Your Code

- **On the Upload Screen**, drag and drop Python files or ZIP archives containing your codebase
- The app accepts `.py` files and `.zip` compressions
- Click **Analyze Workspace** to begin parsing

### 2. Review Coverage

- **Home Screen** shows metrics: total functions, coverage %, undocumented functions, and style breakdown
- Each file appears as a row with function count and coverage stats
- Click a file to expand and see function details

### 3. Validate Docstrings

- Go to the **Validation** tab to run three-layer checks (PEP 257, darglint, AST)
- See detailed error lists keyed by function
- Identify which functions have broken docstrings

### 4. Fix with AI

- In **Validation**, click **Fix Docstrings** on files with errors
- Select your preferred LLM model (Llama, GPT-OSS, Qwen, or Kimi)
- The app calls Groq to repair violations and download the corrected code
- Review and save the fixed version

### 5. Convert Docstring Styles

- Visit the **DocStrings** tab to auto-detect your codebase's style
- See style distribution (Google, NumPy, reST, Mixed)
- Convert entire files or selective functions to a new style via AI

### 6. Generate Tests

- Open the **Dashboard** and navigate to the **Tests** sub-tab
- Click **Generate** to run AI test generation for all functions
- View test code by clicking a function row → **File Tab**
- Tests are cached; regenerate with **Clear Cache** if code changes

### 7. Search & Export

- Use the **Dashboard** search box to find functions by name across all files
- Apply filters: file, style, coverage status, test count
- Click **Export** to download metrics, function lists, or test references as CSV/JSON

### 8. Inspect Help

- Click the **Help (?)** button floating on every screen to see contextual FAQs
- FAQs cover workflow, troubleshooting, and feature limits

---

## Configuration

### Streamlit Settings

Located in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#ffbf00"
backgroundColor = "#121212"
secondaryBackgroundColor = "#1e1e1e"
textColor = "#e0e0e0"

[client]
showErrorDetails = true
```

### Groq Model Selection

Available models in core/fix_code_with_ai.py (`AVAILABLE_MODELS`):

| Model ID | Display Name | Use Case |
|----------|--------------|----------|
| `meta-llama/llama-4-scout-17b-16e-instruct` | 🚀 Llama 4 Scout 17B (Default) | Balanced quality and speed |
| `groq/compound-mini` | ⚡ Compound Mini | Fast, high-throughput option |
| `llama-3.3-70b-versatile` | 🧠 Llama 3.3 70B | Strong general-purpose quality |
| `moonshotai/kimi-k2-instruct` | 🌙 Kimi K2 | Strong structured-output option |
| `openai/gpt-oss-120b` | 🧩 GPT-OSS 120B | Higher quality, slower |
| `openai/gpt-oss-20b` | 🧩 GPT-OSS 20B | Smaller/faster fallback option |

---

## Running Tests

### Full Test Suite

```bash
pytest workspace_tests/fixed workspace_tests/dynamic -q
```

### Individual Test Suites

Health snapshot tests (static validation baseline):

```bash
pytest Test/test_coverage_reporter.py Test/test_dashboard.py Test/test_generator.py -q
pytest Test/test_llm_integration.py Test/test_parser.py Test/test_validation.py -q
```

AI-generated project tests (dynamic):

```bash
pytest workspace_tests/dynamic/ -q
```

### Test Coverage

| File | Purpose | Framework |
|------|---------|-----------|
| **tests/test_darglint.py** | Validates darglint error detection accuracy | pytest |
| **tests/test_pydoc.py** | Validates pydocstyle compliance checking | pytest |
| **Test/test_parser.py** | Tests AST-based function extraction | pytest, unittest.mock |
| **Test/test_coverage_reporter.py** | Tests metric aggregation and reporting | pytest |
| **Test/test_dashboard.py** | Tests dashboard rendering and filtering | pytest |
| **Test/test_generator.py** | Tests docstring generation logic | pytest, unittest.mock |
| **Test/test_llm_integration.py** | Tests Groq API integration | pytest, unittest.mock |
| **Test/test_validation.py** | Tests three-layer validation pipeline | pytest |

**Current Status**: 47 tests, 47 passing (100% success rate)

---

## Known Limitations

- **Streamlit session state**: Workspace data is cleared when the browser tab closes. Download before exiting.
- **LLM rate limits**: Groq has API rate limits. If test generation slows, wait 60 seconds and retry.
- **Large files**: Very large Python files (>10,000 LOC) may take longer to parse; splitting into modules is recommended.
- **Async functions**: Async docstring generation works correctly, but mocking async functions in tests may require pytest-asyncio.
- **Relative imports**: Generated tests assume absolute imports; relative imports in the source may require manual fixes.
- **Test preview**: Test code is shown in read-only mode; copy code to your test folder manually or use export.
- **ZIP extraction**: ZIP archives are extracted to a temporary workspace directory; they are not persisted after app closes.

---

## Contributing

### Reporting Issues

Found a bug or have a feature request? [Open an issue on GitHub](https://github.com/lalith-thexplorer/AI-Powered-Code-Reviewer-and-Quality-Assistant/issues).

### Code Style

- Follow [PEP 8](https://pep8.org/) for all Python code
- New modules go in `core/` (analysis logic) or `faq/` (UI components)
- Test files go in `Test/` directory with naming convention `test_*.py`
- Run the test suite before submitting a PR

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with clear messages
4. Push and open a Pull Request against `main`
5. Ensure all tests pass (`pytest workspace_tests/ -q`)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Credits

Built with:
- [Streamlit](https://streamlit.io/) — rapid Python app framework
- [Groq](https://groq.com/) — fast LLM inference
- [pydocstyle](https://github.com/PyCQA/pydocstyle) — PEP 257 validation
- [darglint](https://github.com/terrencepreilly/darglint) — docstring completeness
- [pytest](https://pytest.org/) — testing framework
- [Plotly](https://plotly.com/) — interactive visualizations

---

## Support

For questions, feedback, or support:
- Check the **Help (?)** button in the app for contextual FAQs
- Review [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) for complete feature documentation
- Review [PROJECT_REPORT.md](PROJECT_REPORT.md) for detailed project report/documentation
- Open an issue on the [GitHub repository](https://github.com/lalith-thexplorer/AI-Powered-Code-Reviewer-and-Quality-Assistant)

---

**Happy reviewing!** 🚀