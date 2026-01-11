"""
GenAgent Pro - Streamlit Web Interface
Interactive web UI for agentic workflow execution
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from core.orchestrator import WorkflowOrchestrator
from utils.logger import setup_logger
import json

# Page config
st.set_page_config(
    page_title="GenAgent Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize environment
@st.cache_resource
def initialize_app():
    """Initialize application (cached)"""
    load_dotenv()
    setup_logger("INFO")
    
    # Create directories
    Path("./data/memory_store").mkdir(parents=True, exist_ok=True)
    Path("./data/logs").mkdir(parents=True, exist_ok=True)
    Path("./data/uploads").mkdir(parents=True, exist_ok=True)
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        return None, "GOOGLE_API_KEY not set in environment"
    
    return True, "Initialized successfully"

@st.cache_resource
def get_orchestrator():
    """Get workflow orchestrator (cached)"""
    return WorkflowOrchestrator()

def main():
    # Header
    st.title("🤖 GenAgent Pro")
    st.markdown("### Agentic AI Workflow Engine")
    st.markdown("*Powered by LangGraph + Google Gemini*")
    
    # Initialize
    status, message = initialize_app()
    
    if status is None:
        st.error(f"❌ Initialization failed: {message}")
        st.info("Please set GOOGLE_API_KEY in your .env file")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        model = st.selectbox(
            "Gemini Model",
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
            index=0
        )
        
        # Temperature
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        
        # Stats
        st.header("📊 System Stats")
        try:
            orchestrator = get_orchestrator()
            stats = orchestrator.vector_store.get_stats()
            st.metric("Memory Vectors", stats["total_vectors"])
            st.metric("Vector Dimension", stats["dimension"])
        except:
            st.info("Stats unavailable")
        
        st.markdown("---")
        
        # Clear memory
        if st.button("🗑️ Clear Memory", type="secondary"):
            try:
                orchestrator = get_orchestrator()
                orchestrator.vector_store.clear()
                st.success("Memory cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear: {e}")
        
        st.markdown("---")
        st.caption("v1.0.0 | Built with LangGraph")
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Task Examples", "📖 Documentation"])
    
    with tab1:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("What would you like me to help with?"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process with agents
            with st.chat_message("assistant"):
                with st.spinner("🤖 Agents working..."):
                    try:
                        orchestrator = get_orchestrator()
                        result = orchestrator.run(prompt)
                        
                        if result["success"]:
                            st.success("✅ Task completed successfully!")
                            st.markdown(result["output"])
                            
                            # Show details in expander
                            with st.expander("📊 Execution Details"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Iterations", result["iterations"])
                                    st.metric("Validation", "✅ PASSED" if result["validation_passed"] else "❌ FAILED")
                                with col2:
                                    st.metric("Errors", len(result["errors"]))
                                    st.metric("Warnings", len(result["warnings"]))
                                
                                if result["errors"]:
                                    st.error("**Errors:**\n" + "\n".join(result["errors"]))
                                if result["warnings"]:
                                    st.warning("**Warnings:**\n" + "\n".join(result["warnings"]))
                        else:
                            st.error("❌ Task failed")
                            st.markdown(result["output"])
                        
                        # Add to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["output"]
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    with tab2:
        st.header("📋 Example Tasks")
        st.markdown("Try these example workflows:")
        
        examples = [
            {
                "title": "📊 Data Analysis",
                "prompt": "Calculate the average of these numbers: 45, 67, 89, 23, 91, 34",
                "description": "Uses calculator tool for computation"
            },
            {
                "title": "🐍 Python Execution",
                "prompt": "Write Python code to generate the first 10 Fibonacci numbers",
                "description": "Executes Python code safely"
            },
            {
                "title": "🔍 Memory Recall",
                "prompt": "What did we talk about in our last conversation?",
                "description": "Searches vector memory for past context"
            },
            {
                "title": "📝 Multi-step Task",
                "prompt": "Calculate 15% of 890, then multiply the result by 3",
                "description": "Demonstrates task decomposition"
            }
        ]
        
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                with st.container(border=True):
                    st.subheader(example["title"])
                    st.caption(example["description"])
                    st.code(example["prompt"], language=None)
                    if st.button(f"Run Example {i+1}", key=f"ex_{i}"):
                        st.session_state.messages.append({
                            "role": "user",
                            "content": example["prompt"]
                        })
                        st.rerun()
    
    with tab3:
        st.header("📖 Documentation")
        
        st.markdown("""
        ## 🤖 GenAgent Pro
        
        An enterprise-grade agentic AI system that autonomously plans, executes, and validates tasks.
        
        ### 🏗️ Architecture
        
        **Agents:**
        - **Planner**: Breaks down goals into executable tasks
        - **Executor**: Executes tasks using available tools
        - **Validator**: Verifies output quality and completeness
        - **Memory**: Manages short and long-term memory
        
        **Tools:**
        - File Reader (PDF, TXT, CSV, DOCX)
        - Python Executor (safe sandboxed execution)
        - Calculator (mathematical expressions)
        - Memory Search (vector similarity search)
        
        **Workflow:**
        1. User provides a goal
        2. Planner creates task breakdown
        3. Executor runs each task with tools
        4. Validator checks quality
        5. Memory stores context
        6. Loop until complete or max retries
        
        ### 🚀 Usage
        
        **CLI Mode:**
        ```bash
        python main.py "Your task here"
        ```
        
        **Interactive CLI:**
        ```bash
        python main.py
        ```
        
        **Web UI:**
        ```bash
        streamlit run app.py
        ```
        
        ### ⚙️ Configuration
        
        Edit `config.yaml` to customize:
        - Agent temperatures
        - Tool settings
        - Memory parameters
        - Workflow limits
        
        ### 🔧 Setup
        
        1. Install dependencies: `pip install -r requirements.txt`
        2. Create `.env` file with `GOOGLE_API_KEY`
        3. Run the application
        
        ### 📝 License
        
        MIT License - Free for commercial use
        """)

if __name__ == "__main__":
    main()