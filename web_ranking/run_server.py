#!/usr/bin/env python
"""
Simple script to run the CDCT Model Ranking web server.

Usage:
    python run_server.py [--port PORT] [--host HOST] [--reload]

Examples:
    python run_server.py
    python run_server.py --port 8080
    python run_server.py --reload  # For development
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run CDCT Model Ranking API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")

    args = parser.parse_args()

    # Check if consolidated results exist
    results_file = Path(__file__).parent.parent / "consolidated_results.json"
    if not results_file.exists():
        print("❌ Error: consolidated_results.json not found!")
        print(f"   Expected location: {results_file}")
        print("\nPlease run the following commands first:")
        print("   cd ..")
        print("   python run_all.py")
        print("   python consolidate_result.py")
        sys.exit(1)

    print("=" * 60)
    print("CDCT Model Ranking API Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers if not args.reload else 1}")
    print("=" * 60)
    print(f"\n🌐 Frontend: http://localhost:{args.port}")
    print(f"📚 API Docs: http://localhost:{args.port}/api/docs")
    print(f"📖 ReDoc: http://localhost:{args.port}/api/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)

    try:
        import uvicorn
        from api.main import app

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=1 if args.reload else args.workers,
            log_level="info"
        )
    except ImportError:
        print("\n❌ Error: Required packages not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
