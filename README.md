# 🤖 Multi-Agent Chatbot

A Streamlit-based chatbot featuring three specialized AI agents, each representing a different company with unique tools and personalities.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)

## 🎯 Features

- **Three Specialized Agents:**
  - 🛒 **ShopBot** (MegaStore E-commerce) - Product search, order tracking
  - 📈 **FinanceBot** (TradePro Securities) - Stock prices, market news
  - 🌤️ **SkyWatch** (GlobalWeather Services) - Weather forecasts, alerts

- **Key Capabilities:**
  - Seamless agent switching without losing chat history
  - OpenAI function calling for intelligent tool usage
  - Beautiful dark-themed UI with gradient backgrounds
  - Separate conversation history per agent
  - Deploy-ready for Streamlit Cloud

## 📁 Project Structure

```
streamlit_bot/
├── app.py                    # Main Streamlit application
├── agents/
│   ├── __init__.py          # Agent configuration exports
│   ├── ecommerce.py         # ShopBot agent & tools
│   ├── stock.py             # FinanceBot agent & tools
│   └── weather.py           # SkyWatch agent & tools
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/streamlit_bot.git
   cd streamlit_bot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Multi-agent chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streamlit_bot.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub repository
4. Select the repository and branch (`main`)
5. Set **Main file path** to `app.py`
6. Click **"Deploy"**

### Step 3: Add Secrets

1. In your deployed app, go to **Settings** → **Secrets**
2. Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```
3. Click **"Save"**

Your app will be available at: `https://your-app-name.streamlit.app`

## 🛠️ Agent Tools

### 🛒 ShopBot (E-commerce)
| Tool | Description |
|------|-------------|
| `search_products()` | Search product catalog by name or category |
| `check_order_status()` | Check order status and delivery info |
| `get_product_details()` | Get detailed product information |

### 📈 FinanceBot (Stock Market)
| Tool | Description |
|------|-------------|
| `get_stock_price()` | Get current stock price and daily change |
| `get_market_summary()` | Overview of major market indices |
| `get_stock_news()` | Latest financial news and market updates |

### 🌤️ SkyWatch (Weather)
| Tool | Description |
|------|-------------|
| `get_weather_forecast()` | Weather forecast for any city |
| `get_weather_alerts()` | Active weather warnings and alerts |
| `get_air_quality()` | Air quality index and health recommendations |

## 💡 Example Queries

### ShopBot
- "Search for wireless headphones"
- "What's the status of order ORD-1001?"
- "Show me details for product ID 3"
- "What electronics do you have under $100?"

### FinanceBot
- "What's the current price of AAPL?"
- "Give me a market summary"
- "Any news about Tesla stock?"
- "How is NVIDIA performing today?"

### SkyWatch
- "What's the weather in New York?"
- "Any weather alerts in Chicago?"
- "Check air quality in Los Angeles"
- "5-day forecast for Miami"

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Streamlit Secrets (for deployment)

Create a `secrets.toml` file or add via Streamlit Cloud dashboard:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

## 🎨 Customization

### Adding New Agents

1. Create a new file in `agents/` (e.g., `agents/support.py`)
2. Define the agent config and tools
3. Export in `agents/__init__.py`
4. The agent will automatically appear in the UI

### Modifying Theme

Edit `.streamlit/config.toml` to customize colors:

```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#your-bg-color"
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you encounter any issues or have questions:
1. Check the [Streamlit documentation](https://docs.streamlit.io/)
2. Review [OpenAI API docs](https://platform.openai.com/docs)
3. Open an issue on GitHub

---

**Built with ❤️ using Streamlit and OpenAI**
