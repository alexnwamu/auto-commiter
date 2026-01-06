#!/usr/bin/env python3
"""Auto-commiter CLI: Generate AI-powered commit messages and commit with one command.

Usage:
    autocommit                 # Generate message, commit, and push
    autocommit --no-push       # Generate and commit without pushing
    autocommit --style verbose # Use verbose commit style
    autocommit config          # Show/change configuration
"""

import argparse
import sys
from typing import Optional

from core import generate_commit_message
from git_utils import add_staged_diff, commit_diff, push_branch, get_staged_diff
from settings import (
    get_setting,
    set_setting,
    get_all_settings,
    reset_settings,
)
from cache import get_cache_stats, clear_cache


def _choose_message(options: list[str]) -> str:
    """Present commit message options and let user choose."""
    print("\n" + "=" * 50)
    print("Select a commit message:")
    print("=" * 50 + "\n")
    
    for idx, msg in enumerate(options, start=1):
        print(f"  [{idx}] {msg}")
        print()
    
    while True:
        choice = input("Enter choice (1/2) or 'q' to cancel: ").strip()
        if choice in {"1", "2"}:
            return options[int(choice) - 1]
        if choice.lower() in {"q", "quit", "exit"}:
            return ""
        print("Invalid choice. Please enter 1, 2, or 'q'.")


def _prompt_edit(message: str) -> str:
    """Allow user to edit the message or accept as-is."""
    print(f"\n📝 Generated message: {message}\n")
    
    response = input("Press Enter to accept, 'e' to edit, or 'q' to cancel: ").strip().lower()
    
    if response == "q":
        return ""
    elif response == "e":
        edited = input("Enter new message: ").strip()
        return edited if edited else message
    return message


def cmd_commit(args) -> int:
    """Main commit command."""
    # Stage changes if requested
    if args.stage:
        print("📁 Staging all changes...")
        if not add_staged_diff():
            print("❌ Failed to stage changes. Aborting.")
            return 1
    
    # Check for staged changes
    diff = get_staged_diff()
    if not diff:
        print("❌ No staged changes. Use 'git add' or run with --stage flag.")
        return 1
    
    # Show diff preview if requested
    if args.preview:
        print("\n" + "=" * 50)
        print("DIFF PREVIEW")
        print("=" * 50)
        if len(diff) > 2000:
            print(diff[:2000])
            print(f"\n... ({len(diff) - 2000} more characters)")
        else:
            print(diff)
        print("=" * 50 + "\n")
    
    # Generate commit message(s)
    print("🤖 Generating commit message...")
    
    if args.single:
        # Generate just one message
        message = generate_commit_message(
            style=args.style,
            use_cache=not args.no_cache,
            model_override=args.model,
        )
        if not message:
            print("❌ Failed to generate commit message. Aborting.")
            return 1
        
        final_message = _prompt_edit(message)
    else:
        # Generate two options
        msg1 = generate_commit_message(
            style=args.style,
            use_cache=not args.no_cache,
            model_override=args.model,
        )
        msg2 = generate_commit_message(
            style=args.style,
            use_cache=False,  # Don't cache second option
            model_override=args.model,
        )
        
        if not msg1 or not msg2:
            print("❌ Failed to generate commit messages. Aborting.")
            return 1
        
        # If both are the same, just show one
        if msg1 == msg2:
            final_message = _prompt_edit(msg1)
        else:
            final_message = _choose_message([msg1, msg2])
    
    if not final_message:
        print("🚫 Commit cancelled.")
        return 0
    
    # Commit
    print("💾 Committing...")
    if not commit_diff(final_message):
        print("❌ git commit failed. Aborting.")
        return 1
    
    print(f"✅ Committed: {final_message}")
    
    # Push if requested
    if args.push:
        print("🚀 Pushing to remote...")
        if not push_branch():
            print("⚠️  git push failed. Your commit is saved locally.")
            return 1
        print("✅ Pushed successfully!")
    
    return 0


def cmd_config(args) -> int:
    """Configuration command."""
    if args.reset:
        reset_settings()
        print("✅ Settings reset to defaults.")
        return 0
    
    if args.key and args.value:
        # Set a specific value
        value = args.value
        # Convert boolean-like strings
        if value.lower() in {"true", "yes", "1", "on"}:
            value = True
        elif value.lower() in {"false", "no", "0", "off"}:
            value = False
        elif value.isdigit():
            value = int(value)
        
        set_setting(args.key, value)
        print(f"✅ Set {args.key} = {value}")
        return 0
    
    # Show all settings
    settings = get_all_settings()
    print("\n📋 Current Configuration:")
    print("-" * 40)
    for key, value in sorted(settings.items()):
        print(f"  {key}: {value}")
    print("-" * 40)
    print("\nUse 'autocommit config <key> <value>' to change a setting.")
    print("Use 'autocommit config --reset' to reset all settings.\n")
    return 0


def cmd_cache(args) -> int:
    """Cache management command."""
    if args.clear:
        clear_cache()
        print("✅ Cache cleared.")
        return 0
    
    # Show cache stats
    stats = get_cache_stats()
    print("\n📊 Cache Statistics:")
    print("-" * 40)
    print(f"  Total entries:  {stats['total_entries']}")
    print(f"  Cache hits:     {stats['hits']}")
    print(f"  Cache misses:   {stats['misses']}")
    print(f"  Hit rate:       {stats['hit_rate']:.1f}%")
    print("-" * 40)
    print("\nUse 'autocommit cache --clear' to clear the cache.\n")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="autocommit",
        description="🚀 Auto-commiter: Generate AI-powered commit messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  autocommit                    # Stage, generate, commit, and push
  autocommit --no-push          # Commit without pushing
  autocommit --style verbose    # Use verbose commit style
  autocommit --model rule-based # Force rule-based model
  autocommit config             # View configuration
  autocommit cache              # View cache stats
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="View/modify configuration")
    config_parser.add_argument("key", nargs="?", help="Setting key to modify")
    config_parser.add_argument("value", nargs="?", help="New value for the setting")
    config_parser.add_argument("--reset", action="store_true", help="Reset all settings to defaults")
    
    # Cache subcommand
    cache_parser = subparsers.add_parser("cache", help="View/manage cache")
    cache_parser.add_argument("--clear", action="store_true", help="Clear the cache")
    
    # Main commit options (default command)
    parser.add_argument(
        "--style", "-s",
        choices=["conventional", "short", "verbose"],
        default=None,
        help="Commit message style (default: from config)",
    )
    parser.add_argument(
        "--model", "-m",
        choices=["auto", "rule-based", "openai"],
        default=None,
        help="Model to use (default: auto)",
    )
    parser.add_argument(
        "--stage", "-a",
        action="store_true",
        default=None,
        help="Stage all changes before committing (git add --all)",
    )
    parser.add_argument(
        "--push", "-p",
        action="store_true",
        default=None,
        help="Push after committing",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push after committing (overrides config)",
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Generate only one message option",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Don't use cached messages",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show diff preview before generating message",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    args = parser.parse_args(argv)
    
    # Handle subcommands
    if args.command == "config":
        return cmd_config(args)
    elif args.command == "cache":
        return cmd_cache(args)
    
    # Default: commit command
    # Apply defaults from settings
    if args.stage is None:
        args.stage = get_setting("auto_stage", True)
    if args.push is None:
        args.push = get_setting("auto_push", False)
    if args.no_push:
        args.push = False
    if args.style is None:
        args.style = get_setting("style", "conventional")
    
    return cmd_commit(args)


if __name__ == "__main__":
    sys.exit(main())
