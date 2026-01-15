from __future__ import annotations

COMMANDS: list[str] = [
    # Navigation
    "open_file",
    "open_folder",
    "recent_files",

    # Search/symbols
    "search_symbols",
    "search_files",
    "go_to_definition",

    # Editing
    "format_document",
    "rename_symbol",
    "extract_function",

    # Version control
    "git_status",
    "git_commit",
    "git_push",
    "git_pull",

    # Testing/build
    "run_tests",
    "run_single_test",
    "build_project",

    # Deployment
    "deploy_staging",
    "deploy_production",
]
