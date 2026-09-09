"""Compatibility entry point for the existing local pre-commit hook."""
from check_current_design import check

if __name__ == "__main__":
    check()
