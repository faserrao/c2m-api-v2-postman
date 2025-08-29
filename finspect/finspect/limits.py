"""Resource limits and security guardrails for finspect."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Ceilings:
    """Resource ceilings for safe operation."""
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    max_bytes_per_file: int = 8192  # 8KB default sniff
    max_zip_entries: int = 10000
    max_total_sniff_bytes: int = 100 * 1024 * 1024  # 100MB total
    max_recursion_depth: int = 1
    timeout_ms: Optional[int] = None
    
    def get_entry_budget(self, num_entries: int) -> int:
        """Calculate byte budget for ZIP entries."""
        total = self.max_bytes_per_file * num_entries
        return min(total, self.max_total_sniff_bytes)


# Default ceilings
DEFAULT_CEILINGS = Ceilings()

# Security constants
MAX_PATH_LENGTH = 4096
MAX_FILENAME_LENGTH = 255