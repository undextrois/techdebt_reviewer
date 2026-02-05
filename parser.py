"""
Markdown file parsing utilities.
"""
import logging
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class MarkdownParser:
    """Parse and discover markdown files."""
    
    @staticmethod
    def discover_markdown_files(
        input_dir: str,
        max_files: Optional[int] = None
    ) -> List[Path]:
        """
        Discover markdown files in a directory.
        
        Args:
            input_dir: Directory to search
            max_files: Maximum number of files to return (for testing)
            
        Returns:
            List of Path objects for markdown files
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")
        
        if not input_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")
        
        # Find all markdown files recursively
        md_files = list(input_path.rglob("*.md"))
        
        # Sort for consistent ordering
        md_files.sort()
        
        # Limit if requested
        if max_files and max_files > 0:
            md_files = md_files[:max_files]
        
        logger.debug(f"Discovered {len(md_files)} markdown files in {input_dir}")
        
        return md_files
    
    @staticmethod
    def read_markdown_file(file_path: Path) -> Tuple[str, str]:
        """
        Read a markdown file and extract its content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Tuple of (content, repo_name)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract repo name from filename
            # Assumes format like "repo_name_review.md" or just "repo_name.md"
            repo_name = file_path.stem.replace('_review', '').replace('_', ' ').title()
            
            logger.debug(f"Read {len(content)} characters from {file_path.name}")
            
            return content, repo_name
        
        except UnicodeDecodeError:
            logger.error(f"Failed to decode {file_path} as UTF-8")
            return "", file_path.stem
        
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return "", file_path.stem
    
    @staticmethod
    def extract_title(markdown_text: str) -> Optional[str]:
        """
        Extract the first H1 title from markdown.
        
        Args:
            markdown_text: Markdown content
            
        Returns:
            Title string or None
        """
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        return None
