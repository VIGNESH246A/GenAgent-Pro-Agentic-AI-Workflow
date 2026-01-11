"""
GenAgent Pro - CLI Entry Point
Command-line interface for agentic workflow execution
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from core.orchestrator import WorkflowOrchestrator
from utils.logger import setup_logger
from loguru import logger


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ███████╗███╗   ██╗ █████╗  ██████╗ ███████╗███╗   ██╗████████╗   ║
║  ██╔════╝ ██╔════╝████╗  ██║██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝   ║
║  ██║  ███╗█████╗  ██╔██╗ ██║███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║      ║
║  ██║   ██║██╔══╝  ██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║      ║
║  ╚██████╔╝███████╗██║ ╚████║██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║      ║
║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                               ║
║             Agentic AI Workflow Engine v1.0                   ║
║                  Powered by LangGraph + Gemini                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def initialize():
    """Initialize environment and configuration"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logger(log_level)
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY not found in environment")
        print("\n❌ Error: GOOGLE_API_KEY not set")
        print("Please create a .env file with your Gemini API key")
        print("Example: GOOGLE_API_KEY=your_key_here")
        sys.exit(1)
    
    # Create data directories
    Path("./data/memory_store").mkdir(parents=True, exist_ok=True)
    Path("./data/logs").mkdir(parents=True, exist_ok=True)
    Path("./data/uploads").mkdir(parents=True, exist_ok=True)
    
    logger.info("Environment initialized successfully")


def print_result(result: dict):
    """Pretty print workflow result"""
    print("\n" + "="*70)
    print("📊 WORKFLOW RESULT")
    print("="*70)
    
    if result["success"]:
        print("✅ Status: SUCCESS")
    else:
        print("❌ Status: FAILED")
    
    print(f"🔄 Iterations: {result['iterations']}")
    print(f"✓ Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
    
    print("\n📝 Output:")
    print("-" * 70)
    print(result["output"])
    print("-" * 70)
    
    if result["errors"]:
        print("\n❌ Errors:")
        for error in result["errors"]:
            print(f"  • {error}")
    
    if result["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in result["warnings"]:
            print(f"  • {warning}")
    
    print("\n" + "="*70 + "\n")


def run_interactive():
    """Interactive CLI mode"""
    print_banner()
    print("\n🤖 Interactive Mode - Type 'exit' to quit\n")
    
    # Initialize
    initialize()
    
    # Create orchestrator
    print("🔧 Initializing agents...")
    orchestrator = WorkflowOrchestrator()
    print("✅ Ready!\n")
    
    # Interactive loop
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🔄 Processing...\n")
            
            # Execute workflow
            result = orchestrator.run(user_input)
            
            # Display result
            print_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n❌ Error: {e}\n")


def run_single_query(query: str):
    """Execute single query and exit"""
    initialize()
    
    print("🔧 Initializing agents...")
    orchestrator = WorkflowOrchestrator()
    
    print(f"\n📥 Query: {query}\n")
    print("🔄 Processing...\n")
    
    result = orchestrator.run(query)
    print_result(result)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        run_single_query(query)
    else:
        # Interactive mode
        run_interactive()


if __name__ == "__main__":
    main()