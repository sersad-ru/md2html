#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################
# ************************
# * md2html by sersad *
# ************************
# Конвертер readme.md в html
# со стилями github
# (c)2026 by sersad@gmail.com
# 06.09.2026
##############################
#
# pyinstaller --onefile --name md2html --clean --hidden-import=markdown_it --hidden-import=mdit_py_plugins.gfm md2html.py
#

"""
md2html - Convert Markdown files to HTML with GitHub styling

Usage:
    python md2html.py [options]

Options:
    -i, --input INPUT     Input markdown file (default: README.md)
    -o, --output OUTPUT   Output HTML file (default: index.html)
    -l, --local           Embed CSS locally instead of using CDN
    --version             Show version and exit
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Import markdown-it-py and plugins
try:
    from markdown_it import MarkdownIt
    from mdit_py_plugins.gfm import gfm_plugin
    
    HAS_DEPS = True
except ImportError as e:
    HAS_DEPS = False
    DEPS_ERROR = str(e)

__version__ = "1.0.0"

# GitHub CSS from jsDelivr CDN (version 5.2.0)
GITHUB_CSS_URL = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.2.0/github-markdown.min.css"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to HTML with GitHub styling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python md2html.py                    # Convert README.md to index.html
    python md2html.py -i docs/readme.md -o docs/index.html
    python md2html.py -l                 # Embed CSS locally
    python md2html.py --version
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        default="README.md",
        help="Input markdown file (default: README.md)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="index.html",
        help="Output HTML file (default: index.html)"
    )
    
    parser.add_argument(
        "-l", "--local",
        action="store_true",
        help="Embed CSS locally instead of using CDN"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"md2html {__version__}"
    )
    
    return parser.parse_args()


def validate_files(input_path: str, output_path: str) -> tuple[Path, Path]:
    """Validate input and output file paths."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    # Check if input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Check if input file has .md extension
    if input_file.suffix.lower() != ".md":
        print(f"Warning: Input file doesn't have .md extension: {input_file}")
    
    # Check if output file has .html extension
    if output_file.suffix.lower() != ".html":
        print(f"Warning: Output file doesn't have .html extension: {output_file}")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    return input_file, output_file


def read_markdown_file(file_path: Path) -> str:
    """Read markdown file with UTF-8 encoding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        print(f"Warning: UTF-8 decoding failed for {file_path}, trying latin-1")
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()


def write_html_file(file_path: Path, content: str) -> None:
    """Write HTML file with UTF-8 encoding."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise RuntimeError(f"Failed to write output file {file_path}: {e}")


def convert_markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML using GitHub Flavored Markdown."""
    if not HAS_DEPS:
        raise ImportError(
            f"Missing required dependencies. Please install with:\n"
            f"pip install markdown-it-py\n"
            f"Original error: {DEPS_ERROR}"
        )
    
    # Initialize markdown-it with GFM extensions
    md = MarkdownIt("commonmark")
    
    # Add GFM plugin (includes tables, tasklists, strikethrough, autolinks, etc.)
    md.use(gfm_plugin)
    
    # Enable HTML tags (for GitHub's custom markup)
    md.enable("html_inline")
    md.enable("html_block")
    
    # Convert markdown to HTML
    html = md.render(markdown_content)
    
    # Post-process: Add ID attributes to headers and fix anchor links
    import re
    import urllib.parse
    
    # Create slug from header text (matches GitHub's behavior)
    def make_slug(text):
        # Normalize hyphen-like Unicode characters to regular ASCII hyphen
        # U+2010 HYPHEN, U+2011 NON-BREAKING HYPHEN, U+2012 FIGURE DASH,
        # U+2013 EN DASH, U+2014 EM DASH, U+2015 HORIZONTAL BAR
        text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', text)
        # Convert to lowercase
        slug = text.lower()
        # Keep only alphanumeric (including Cyrillic), whitespace, and dashes
        # \w in Python matches Unicode word characters, so it includes Cyrillic
        slug = re.sub(r'[^\w\s-]', '', slug)
        # Replace whitespace with dashes
        slug = re.sub(r'[\s]+', '-', slug)
        # Remove multiple dashes
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing dashes
        slug = slug.strip('-')
        return slug
    
    # Add ID attributes to headers (h1-h6) based on their text content
    def add_id_to_header(match):
        tag = match.group(1)  # h1, h2, etc.
        content = match.group(2)
        
        # Create slug from header text
        slug = make_slug(content)
        
        return f'<h{tag} id="{slug}">{content}</h{tag}>'
    
    # Add IDs to headers that don't have them
    html = re.sub(r'<h([1-6])>([^<]+)</h\1>', add_id_to_header, html)
    
    # Fix URL-encoded Cyrillic characters in href attributes
    # Header IDs are NOT URL-encoded (raw Cyrillic), so href must match
    def fix_href(match):
        href = match.group(1)
        # If href is URL-encoded, decode it to match header IDs
        if '%' in href:
            decoded = urllib.parse.unquote(href)
            return f'href="#{decoded}"'
        # Already plain, leave as is
        return match.group(0)
    
    # Pattern to match href attributes in anchor tags
    html = re.sub(r'href="#([^"]*)"', fix_href, html)
    
    return html


def fetch_css_from_cdn() -> str:
    """Fetch GitHub CSS from CDN."""
    import urllib.request
    
    print("Fetching GitHub CSS from CDN...")
    try:
        with urllib.request.urlopen(GITHUB_CSS_URL, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch CSS from CDN: {e}")


def get_css_content(local: bool = False) -> tuple[str, bool]:
    """Get GitHub CSS content.
    
    Returns:
        tuple: (css_content_or_link, is_embedded)
    """
    if local:
        # Fetch and embed CSS locally
        css = fetch_css_from_cdn()
        return css, True
    else:
        # Return CDN link
        css_link = f'<link rel="stylesheet" href="{GITHUB_CSS_URL}">'
        return css_link, False


def generate_html_document(
    content: str,
    filename: str,
    css_content: str,
    css_embedded: bool = False
) -> str:
    """Generate complete HTML document with GitHub styling."""
    # Determine language based on filename or default to Russian
    lang = "ru" if "README" in filename.upper() else "en"
    
    # CSS section
    if css_embedded:
        css_section = f'<style>\n{css_content}\n</style>'
    else:
        css_section = css_content
    
    # Complete HTML document
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    {css_section}
    <style>
        /* Custom adjustments for better GitHub compatibility */
        .markdown-body {{
            box-sizing: border-box;
            min-width: 200px;
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
        }}
        
        @media (max-width: 767px) {{
            .markdown-body {{
                padding: 15px;
            }}
        }}
        
        /* Ensure tables work properly */
        .markdown-body table {{
            display: block;
            width: 100%;
            overflow: auto;
            word-break: normal;
            word-break: keep-all;
        }}
        
        /* Anchor links */
        .anchor {{
            float: left;
            padding-right: 4px;
            margin-left: -20px;
            text-decoration: none;
        }}
        
        .anchor:hover {{
            text-decoration: none;
        }}
        
        h1 .anchor,
        h2 .anchor,
        h3 .anchor,
        h4 .anchor,
        h5 .anchor,
        h6 .anchor {{
            visibility: hidden;
        }}
        
        h1:hover .anchor,
        h2:hover .anchor,
        h3:hover .anchor,
        h4:hover .anchor,
        h5:hover .anchor,
        h6:hover .anchor {{
            visibility: visible;
        }}
    </style>
</head>
<body>
    <article class="markdown-body entry-content container-lg" itemprop="text">
        {content}
    </article>
</body>
</html>"""
    
    return html


def main() -> None:
    """Main function."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Validate and prepare file paths
        input_file, output_file = validate_files(args.input, args.output)
        
        print(f"Converting {input_file} to {output_file}...")
        
        # Read markdown file
        markdown_content = read_markdown_file(input_file)
        
        # Convert markdown to HTML
        html_content = convert_markdown_to_html(markdown_content)
        
        # Get CSS content
        css_content, css_embedded = get_css_content(args.local)
        
        # Generate complete HTML document
        full_html = generate_html_document(
            html_content,
            input_file.name,
            css_content,
            css_embedded
        )
        
        # Write output file
        write_html_file(output_file, full_html)
        
        # Print success message
        mode = "embedded" if css_embedded else "CDN"
        success_msg = f"OK: {input_file} -> {output_file}"
        print(success_msg)
        print(f"  CSS mode: {mode}")
        print(f"  Output file size: {output_file.stat().st_size} bytes")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()