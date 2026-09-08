# md2html

A lightweight Python utility to convert Markdown files to HTML with authentic **GitHub styling**. Perfect for generating standalone HTML documentation from README files or any Markdown content.

## Features

- 🎨 **GitHub-flavored Markdown** — Full GFM support (tables, task lists, strikethrough, autolinks, code blocks)
- 🎯 **Authentic GitHub styling** — Uses official `github-markdown-css` for pixel-perfect rendering
- 🌐 **Two CSS modes** — Embed CSS locally (`-l` flag) for offline use, or link to CDN for smaller HTML files
- 🇷🇺 **Full Unicode/Russian support** — Handles Cyrillic and other Unicode characters correctly
- 📦 **Zero-config defaults** — Run `python md2html.py` and it just works (README.md → index.html)
- 🔧 **CLI flexibility** — Custom input/output paths, version flag
- 📦 **Standalone executable** — Build with PyInstaller for distribution without Python dependencies

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Convert README.md to index.html (default behavior)
python md2html.py

# Custom input/output
python md2html.py -i docs/readme.md -o docs/index.html

# Embed CSS locally (works offline)
python md2html.py -l
```

## Installation

### From Source

```bash
git clone https://github.com/yourusername/md2html.git
cd md2html
pip install -r requirements.txt
```

### As Standalone Executable

Download the latest release or build yourself:

```bash
pip install pyinstaller
pyinstaller --onefile --name md2html md2html.py
# Executable will be in ./dist/md2html (or ./dist/md2html.exe on Windows)
```

## Usage

```bash
md2html.py [-h] [-i INPUT] [-o OUTPUT] [-l] [--version]
```

### Options

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-i` | `--input` | Input Markdown file | `README.md` |
| `-o` | `--output` | Output HTML file | `index.html` |
| `-l` | `--local` | Embed CSS locally (offline mode) | `False` (uses CDN) |
| | `--version` | Show version and exit | |

### Examples

```bash
# Basic usage (README.md → index.html)
python md2html.py

# Convert specific file
python md2html.py -i CHANGELOG.md -o changelog.html

# Offline-ready HTML with embedded CSS
python md2html.py -l -i README.md -o README.html

# Process documentation folder
python md2html.py -i docs/guide.md -o docs/guide.html -l
```

## Requirements

- Python 3.8+
- `markdown-it-py` ≥ 3.0.0 — GitHub-flavored Markdown parser
- `mdit-py-plugins` ≥ 0.6.0 — GFM extensions (tables, tasklists, etc.)

Install with:
```bash
pip install -r requirements.txt
```

## Building Standalone Executable

```bash
# Install build dependencies
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --name md2html md2html.py

# With explicit hidden imports (if needed)
pyinstaller --onefile --name md2html \
    --hidden-import=markdown_it \
    --hidden-import=mdit_py_plugins.gfm \
    md2html.py
```

The executable will be in `./dist/md2html` (or `./dist/md2html.exe` on Windows).

**Expected size:** ~8-12 MB  
**Compatibility:** No external data files needed at runtime (CSS is embedded or fetched from CDN)

## How It Works

1. **Parses CLI arguments** with sensible defaults
2. **Reads Markdown file** with UTF-8 encoding (falls back to latin-1)
3. **Converts to HTML** using `markdown-it-py` with GFM plugin
4. **Adds GitHub-style anchor IDs** to headers (h1-h6)
5. **Generates complete HTML5 document** with:
   - Proper meta tags (charset, viewport)
   - GitHub markdown container classes (`.markdown-body`, `.entry-content`, `.container-lg`)
   - GitHub CSS (embedded or CDN link)
   - Custom adjustments for responsive tables, anchor links
6. **Writes output file** with UTF-8 encoding

## Supported Markdown Features

| Feature | Example |
|---------|---------|
| Headers | `# H1` through `###### H6` |
| Tables | `\| a \| b \|\n\|---\|---\|\n\| 1 \| 2 \|` |
| Task Lists | `- [ ] Todo` / `- [x] Done` |
| Strikethrough | `~~deleted~~` |
| Code Blocks | ```python\ncode\n``` |
| Inline Code | `` `code` `` |
| Links | `[text](url)` |
| Images | `![alt](image.png)` |
| Blockquotes | `> quote` |
| Lists | `- item` / `1. item` |
| Horizontal Rule | `---` |

## Output HTML Structure

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README.md</title>
    <!-- CSS: embedded <style> or <link rel="stylesheet" href="..."> -->
    <style>
        /* GitHub markdown CSS + custom adjustments */
    </style>
</head>
<body>
    <article class="markdown-body entry-content container-lg" itemprop="text">
        <!-- Converted markdown content -->
    </article>
</body>
</html>
```

## Language Detection

The script automatically sets the HTML `lang` attribute:
- `lang="ru"` if filename contains "README" (case-insensitive)
- `lang="en"` otherwise

## Troubleshooting

### "Missing required dependencies"
```bash
pip install markdown-it-py mdit-py-plugins
```

### "Input file not found"
Ensure the input file exists and path is correct:
```bash
python md2html.py -i path/to/file.md
```

### CSS not loading (offline mode)
Use the `-l` flag to embed CSS locally:
```bash
python md2html.py -l -i README.md -o index.html
```

### Cyrillic characters in anchor links
The script automatically URL-encodes Cyrillic characters in header IDs and anchor links for proper HTML compliance.

## License

MIT License — feel free to use, modify, and distribute.

## Author

**sersad** — sersad@gmail.com

---

*Generated with md2html v1.0.0*