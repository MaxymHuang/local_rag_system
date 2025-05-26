# Local RAG File Finder

This is a local Retrieval Augmented Generation (RAG) system that helps you find files and directories using natural language queries. The system uses sentence embeddings and FAISS for efficient similarity search.

## Features

- Natural language search for files and directories
- Semantic understanding of file and directory descriptions
- Relevance scoring for search results
- Interactive command-line interface
- Windows-compatible path handling
- Error handling for Windows-specific issues

## Setup

1. Create a virtual environment (recommended):

   **Option 1 - Using PowerShell:**
   ```powershell
   python -m venv venv
   # If you get an execution policy error, run this first:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\activate
   ```

   **Option 2 - Using Command Prompt:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Usage

1. Run the script:
```powershell
python file_finder.py 
# add --root-dir "path/to/directory" to specify root directory
```

2. The system will first build an index of your file system (this may take a few moments depending on the size of your directory).

3. Once the index is built, you can enter natural language queries to find files and directories. For example:
   - "Find all Python files"
   - "Show me directories containing documentation"
   - "Where are the configuration files?"

4. Type 'quit' to exit the program.

## Windows-Specific Notes

- The system uses Windows-style path separators
- Hidden files and directories (starting with '.') are automatically skipped
- Long file paths are supported
- The system handles Windows-specific file system errors gracefully

### PowerShell Execution Policy

If you encounter a PowerShell execution policy error when activating the virtual environment, you have two options:

1. **Temporary Solution** (recommended):
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\activate
   ```

2. **Alternative Solution**:
   - Use Command Prompt (cmd.exe) instead of PowerShell
   - Run: `venv\Scripts\activate.bat`

## How it Works

1. The system creates a semantic index of your file system by:
   - Walking through all directories and files
   - Generating descriptions for each file and directory
   - Creating embeddings using the SentenceTransformer model

2. When you search:
   - Your query is converted to an embedding
   - The system finds the most similar file/directory descriptions
   - Results are ranked by relevance score

## Requirements

- Windows 10 or later
- Python 3.7+
- Dependencies listed in requirements.txt

## Troubleshooting

If you encounter any issues:

1. Make sure you're running the script from a directory with appropriate permissions
2. Check that your Python environment is properly activated
3. Verify that all dependencies are installed correctly
4. If you get path-related errors, try using absolute paths instead of relative paths
5. If you get PowerShell execution policy errors, see the "PowerShell Execution Policy" section above 