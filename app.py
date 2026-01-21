"""
Multi-Agent Chatbot Application
A Streamlit-based chatbot with three specialized agents:
- ShopBot (E-commerce)
- FinanceBot (Stock Market)
- SkyWatch (Weather) - with MCP Weather Server integration

Author: Built with Cursor AI
"""

import streamlit as st
import asyncio
import json
import os
import inspect
import logging
import atexit
from openai import OpenAI

from agents import AGENTS, TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# MCP Server Initialization (Weather & Stock)
# =============================================================================

@st.cache_resource
def initialize_mcp_weather_client():
    """
    Initialize the MCP Weather Client as a singleton resource.
    Uses @st.cache_resource to ensure only one instance across reruns.
    
    Returns:
        MCPWeatherClient instance or None if unavailable
    """
    try:
        from mcp_client import get_weather_client
        client = get_weather_client()
        logger.info("MCP Weather Client initialized successfully")
        return client
    except ImportError as e:
        logger.warning(f"MCP Weather Client not available (missing dependencies): {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize MCP Weather Client: {e}")
        return None


@st.cache_resource
def initialize_mcp_stock_client():
    """
    Initialize the MCP Stock Client as a singleton resource.
    Uses @st.cache_resource to ensure only one instance across reruns.
    
    Returns:
        MCPStockClient instance or None if unavailable
    """
    try:
        from mcp_client import get_stock_client
        client = get_stock_client()
        logger.info("MCP Stock Client initialized successfully")
        return client
    except ImportError as e:
        logger.warning(f"MCP Stock Client not available (missing dependencies): {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize MCP Stock Client: {e}")
        return None


def cleanup_mcp_clients():
    """Cleanup MCP clients on application shutdown."""
    try:
        from mcp_client import shutdown_weather_client
        shutdown_weather_client()
        logger.info("MCP Weather Client shutdown complete")
    except Exception as e:
        logger.error(f"Error during MCP Weather client cleanup: {e}")
    
    try:
        from mcp_client.stock_client import shutdown_stock_client
        shutdown_stock_client()
        logger.info("MCP Stock Client shutdown complete")
    except Exception as e:
        logger.error(f"Error during MCP Stock client cleanup: {e}")


# Register cleanup function
atexit.register(cleanup_mcp_clients)

# Initialize MCP clients (will be cached)
_mcp_weather_client = initialize_mcp_weather_client()
_mcp_stock_client = initialize_mcp_stock_client()

# Inject stock client into stock agent
try:
    from agents.stock import set_stock_client
    set_stock_client(_mcp_stock_client)
    logger.info("MCP Stock Client injected into stock agent")
except Exception as e:
    logger.error(f"Failed to inject stock client: {e}")

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Multi-Agent Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS Styling
# =============================================================================
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #333;
    }
    
    /* Agent selection buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Tool display in sidebar */
    .tool-badge {
        background: rgba(255,255,255,0.1);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85em;
        margin: 2px;
        display: inline-block;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Agent card in sidebar */
    .agent-info {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    /* Spinner custom color */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #666;
        padding: 20px;
        font-size: 0.9em;
    }
    
    /* MCP status indicator */
    .mcp-status {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.75em;
        display: inline-block;
        margin-top: 5px;
    }
    .mcp-active {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid #2ecc71;
    }
    .mcp-inactive {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
        border: 1px solid #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Helper Functions
# =============================================================================

def get_api_key() -> str:
    """Retrieve OpenAI API key from Streamlit secrets or environment variables."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY", "")


def get_tool_definitions(tools: list) -> list:
    """Convert tool functions to OpenAI function calling format."""
    definitions = []
    
    for tool in tools:
        sig = inspect.signature(tool)
        params = {}
        required = []
        
        # Parse function parameters
        for name, param in sig.parameters.items():
            # Determine parameter type
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            # Extract description from docstring if available
            doc = tool.__doc__ or ""
            param_desc = f"Parameter: {name}"
            
            # Try to find parameter description in docstring
            if f"{name}:" in doc:
                for line in doc.split("\n"):
                    if f"{name}:" in line:
                        param_desc = line.split(":", 1)[-1].strip()
                        break
            
            params[name] = {
                "type": param_type,
                "description": param_desc
            }
            
            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        # Build function definition
        definitions.append({
            "type": "function",
            "function": {
                "name": tool.__name__,
                "description": tool.__doc__.split("\n")[0] if tool.__doc__ else f"Execute {tool.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required
                }
            }
        })
    
    return definitions


async def execute_tool(tool_name: str, tools: list, args: dict) -> dict:
    """Execute a tool function by name with given arguments."""
    tools_map = {t.__name__: t for t in tools}
    
    if tool_name in tools_map:
        try:
            result = await tools_map[tool_name](**args)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    return {"error": f"Tool '{tool_name}' not found"}


def get_chat_response(
    user_message: str,
    chat_history: list,
    agent_config: dict,
    tools: list
) -> str:
    """Generate a response using OpenAI with function calling."""
    api_key = get_api_key()
    
    if not api_key:
        return """⚠️ **API Key Required**
        
Please set your OpenAI API key to enable the chatbot:

**For local development:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**For Streamlit Cloud:**
Add `OPENAI_API_KEY` in Settings → Secrets"""
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Build tool definitions
        tool_definitions = get_tool_definitions(tools)
        
        # Build message history
        messages = [
            {"role": "system", "content": agent_config["description"]}
        ]
        
        # Add recent chat history (last 10 messages for context)
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # First API call - may include tool calls
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tool_definitions if tool_definitions else None,
            tool_choice="auto" if tool_definitions else None,
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_message = response.choices[0].message
        
        # Check if the model wants to use tools
        if assistant_message.tool_calls:
            # Add assistant message with tool calls to history
            messages.append(assistant_message)
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                tool_result = asyncio.run(execute_tool(tool_name, tools, tool_args))
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, indent=2)
                })
            
            # Second API call - generate final response with tool results
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return final_response.choices[0].message.content
        
        return assistant_message.content
        
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "❌ **Authentication Error**: Please check your OpenAI API key."
        elif "rate_limit" in error_msg.lower():
            return "⏳ **Rate Limited**: Too many requests. Please wait a moment and try again."
        else:
            return f"❌ **Error**: {error_msg}"


# =============================================================================
# Session State Initialization
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = {agent_id: [] for agent_id in AGENTS.keys()}

if "current_agent" not in st.session_state:
    st.session_state.current_agent = "ecommerce"

# =============================================================================
# Sidebar - Agent Selection
# =============================================================================

with st.sidebar:
    st.markdown("## 🤖 Multi-Agent Hub")
    st.markdown("---")
    
    st.markdown("### Choose Your Assistant")
    st.caption("Each agent specializes in different tasks")
    
    # Agent selection buttons
    for agent_id, config in AGENTS.items():
        # Determine if this agent is selected
        is_selected = st.session_state.current_agent == agent_id
        button_type = "primary" if is_selected else "secondary"
        
        # Create button with agent info
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"### {config['icon']}")
        with col2:
            if st.button(
                f"{config['name']}\n{config['company']}",
                key=f"btn_{agent_id}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_agent = agent_id
                st.rerun()
    
    st.markdown("---")
    
    # Current agent details
    current_config = AGENTS[st.session_state.current_agent]
    current_tools = TOOLS[st.session_state.current_agent]
    
    st.markdown(f"### 📋 Active Agent")
    
    # Agent info card
    st.markdown(f"""
    <div class="agent-info" style="border-color: {current_config['color']};">
        <h4>{current_config['icon']} {current_config['name']}</h4>
        <p style="color: #888; font-size: 0.9em;">{current_config['company']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Available tools
    st.markdown("**🛠️ Available Tools:**")
    for tool in current_tools:
        st.markdown(f"- `{tool.__name__}()`")
    
    # Show MCP status for weather agent
    if st.session_state.current_agent == "weather":
        st.markdown("---")
        st.markdown("**📡 Data Source:**")
        if _mcp_weather_client is not None:
            st.markdown('<span class="mcp-status mcp-active">🟢 MCP Server Active</span>', unsafe_allow_html=True)
            st.caption("Using Open-Meteo live data")
        else:
            st.markdown('<span class="mcp-status mcp-inactive">🔴 MCP Unavailable</span>', unsafe_allow_html=True)
            st.caption("Using mock data fallback")
    
    # Show MCP status for stock agent
    if st.session_state.current_agent == "stock":
        st.markdown("---")
        st.markdown("**📡 Data Source:**")
        if _mcp_stock_client is not None:
            st.markdown('<span class="mcp-status mcp-active">🟢 MCP Server Active</span>', unsafe_allow_html=True)
            st.caption("Using Yahoo Finance live data")
        else:
            st.markdown('<span class="mcp-status mcp-inactive">🔴 MCP Unavailable</span>', unsafe_allow_html=True)
            st.caption("Service unavailable")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages[st.session_state.current_agent] = []
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("Built with Streamlit & OpenAI")
    st.caption("v1.1.0 - MCP Integration")

# =============================================================================
# Main Chat Interface
# =============================================================================

# Get current agent config
current_config = AGENTS[st.session_state.current_agent]
current_tools = TOOLS[st.session_state.current_agent]

# Header
st.markdown(f"# {current_config['icon']} Chat with {current_config['name']}")
st.markdown(f"**{current_config['company']}** | Your AI-powered assistant")
st.markdown("---")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages[st.session_state.current_agent]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Welcome message if no chat history
if not st.session_state.messages[st.session_state.current_agent]:
    with st.chat_message("assistant"):
        welcome_messages = {
            "ecommerce": "👋 Welcome to MegaStore! I'm **ShopBot**, your personal shopping assistant. I can help you:\n\n- 🔍 **Search products** in our catalog\n- 📦 **Track your orders** \n- 📋 **Get product details** and recommendations\n\nHow can I help you today?",
            "stock": "📊 Welcome to TradePro Securities! I'm **FinanceBot**, your financial information assistant. I can help you:\n\n- 💹 **Get stock prices** and daily changes\n- 📈 **View market summaries** and indices\n- 📰 **Read financial news**\n\n" + ("📡 *Live data from Yahoo Finance*" if _mcp_stock_client else "⚠️ *Stock data service unavailable*") + "\n\n*Disclaimer: Information provided is for educational purposes only and not financial advice.*\n\nWhat would you like to know?",
            "weather": "🌤️ Hello! I'm **SkyWatch** from GlobalWeather Services. I can help you:\n\n- 🌡️ **Check weather forecasts** for any city (powered by Open-Meteo)\n- ⚠️ **View weather alerts** and warnings\n- 💨 **Check air quality** information\n\n" + ("📡 *Live data from MCP Weather Server*" if _mcp_weather_client else "📊 *Using simulated weather data*") + "\n\nWhich city's weather would you like to know about?"
        }
        st.markdown(welcome_messages.get(st.session_state.current_agent, "Hello! How can I help you?"))

# Chat input
if prompt := st.chat_input(f"Ask {current_config['name']} anything..."):
    # Add user message to history
    st.session_state.messages[st.session_state.current_agent].append({
        "role": "user",
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner(f"{current_config['name']} is thinking..."):
            response = get_chat_response(
                user_message=prompt,
                chat_history=st.session_state.messages[st.session_state.current_agent],
                agent_config=current_config,
                tools=current_tools
            )
            st.markdown(response)
    
    # Add assistant response to history
    st.session_state.messages[st.session_state.current_agent].append({
        "role": "assistant",
        "content": response
    })

# =============================================================================
# Footer
# =============================================================================

st.markdown("---")
st.markdown(
    f"""
    <div class="footer">
        <p>🤖 <strong>Multi-Agent Hub</strong> | Currently chatting with {current_config['icon']} {current_config['name']}</p>
        <p>Powered by OpenAI GPT-4o-mini | Built with Streamlit</p>
        <p style="font-size: 0.8em; color: #555;">Weather: {'MCP (Open-Meteo)' if _mcp_weather_client else 'Mock'} | Stock: {'MCP (Yahoo Finance)' if _mcp_stock_client else 'Unavailable'}</p>
    </div>
    """,
    unsafe_allow_html=True
)
