#!/usr/bin/env python3
"""
Simple CLI interface for TalkShow.

Basic commands to demonstrate CLI functionality.
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to path so we can import talkshow
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow.parser.md_parser import MDParser
from talkshow.storage.json_storage import JSONStorage


def cmd_parse(args):
    """Parse command: parse MD files from directory."""
    print(f"📁 Parsing files from '{args.directory}'...")
    
    parser = MDParser()
    sessions = parser.parse_directory(args.directory)
    
    if not sessions:
        print("❌ No valid sessions found!")
        return 1
    
    print(f"✅ Found {len(sessions)} valid chat sessions")
    
    if args.output:
        storage = JSONStorage(args.output)
        if storage.save_sessions(sessions):
            print(f"💾 Sessions saved to '{args.output}'")
        else:
            print("❌ Failed to save sessions!")
            return 1
    
    return 0


def cmd_list(args):
    """List command: list all stored sessions."""
    if not Path(args.storage).exists():
        print(f"❌ Storage file not found: {args.storage}")
        return 1
    
    storage = JSONStorage(args.storage)
    sessions = storage.load_all_sessions()
    
    if not sessions:
        print("📭 No sessions found in storage")
        return 0
    
    print(f"📋 Found {len(sessions)} sessions:")
    print("-" * 60)
    
    for i, session in enumerate(sessions, 1):
        print(f"{i:2d}. {session.meta.theme}")
        print(f"    File: {session.meta.filename}")
        print(f"    Time: {session.meta.ctime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Q&A pairs: {len(session.qa_pairs)}")
        print()
    
    return 0


def cmd_show(args):
    """Show command: display details of a specific session."""
    if not Path(args.storage).exists():
        print(f"❌ Storage file not found: {args.storage}")
        return 1
    
    storage = JSONStorage(args.storage)
    session = storage.load_session(args.filename)
    
    if not session:
        print(f"❌ Session not found: {args.filename}")
        return 1
    
    print(f"📄 Session: {session.meta.theme}")
    print(f"📁 File: {session.meta.filename}")
    print(f"⏰ Time: {session.meta.ctime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💬 Q&A pairs: {len(session.qa_pairs)}")
    print("-" * 60)
    
    for i, qa_pair in enumerate(session.qa_pairs, 1):
        print(f"\n🔹 Q&A Pair {i}:")
        print(f"❓ Q: {qa_pair.question[:100]}{'...' if len(qa_pair.question) > 100 else ''}")
        print(f"💡 A: {qa_pair.answer[:200]}{'...' if len(qa_pair.answer) > 200 else ''}")
        if qa_pair.timestamp:
            print(f"⏱️  Time: {qa_pair.timestamp.strftime('%H:%M:%S')}")
    
    return 0


def cmd_stats(args):
    """Stats command: show storage statistics."""
    if not Path(args.storage).exists():
        print(f"❌ Storage file not found: {args.storage}")
        return 1
    
    storage = JSONStorage(args.storage)
    sessions = storage.load_all_sessions()
    info = storage.get_storage_info()
    
    total_qa_pairs = sum(len(session.qa_pairs) for session in sessions)
    
    print("📊 TalkShow Statistics")
    print("=" * 30)
    print(f"Total sessions: {len(sessions)}")
    print(f"Total Q&A pairs: {total_qa_pairs}")
    print(f"Storage file size: {info.get('file_size_bytes', 0):,} bytes")
    
    if sessions:
        avg_qa_per_session = total_qa_pairs / len(sessions)
        print(f"Average Q&A per session: {avg_qa_per_session:.1f}")
        
        oldest = min(sessions, key=lambda s: s.meta.ctime)
        newest = max(sessions, key=lambda s: s.meta.ctime)
        print(f"Date range: {oldest.meta.ctime.strftime('%Y-%m-%d')} to {newest.meta.ctime.strftime('%Y-%m-%d')}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="TalkShow - Chat History Analysis Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse MD files from directory")
    parse_parser.add_argument("directory", help="Directory containing MD files")
    parse_parser.add_argument("-o", "--output", help="Output JSON file")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all stored sessions")
    list_parser.add_argument("-s", "--storage", default="data/parsed_sessions.json", help="Storage JSON file")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a specific session")
    show_parser.add_argument("filename", help="Filename of the session to show")
    show_parser.add_argument("-s", "--storage", default="data/parsed_sessions.json", help="Storage JSON file")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show storage statistics")
    stats_parser.add_argument("-s", "--storage", default="data/parsed_sessions.json", help="Storage JSON file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == "parse":
        return cmd_parse(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "stats":
        return cmd_stats(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())