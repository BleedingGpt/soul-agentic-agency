"""S.O.U.L. — Sacrifice Outweighs Ultimate Leverage. Central config."""
import os

# Brain: ONE env var swaps it. Default = strongest reasoning, zero local RAM (Ollama cloud, needs internet).
#   default:      gpt-oss:120b-cloud (OpenAI open-weight 120B, clean JSON + separate thinking field)
#   offline:      llama3.2:3b (2GB local, proven clean output on this machine)
#   strong local: qwen2.5-coder:7b
# Rejected: qwen3:4b + deepseek-r1 (emit chain-of-thought as content, breaks the JSON protocol).
MODEL = os.getenv("SOUL_MODEL", "gpt-oss:120b-cloud")
OLLAMA_URL = os.getenv("SOUL_OLLAMA_URL", "http://localhost:11434")

# Loop guardrails (utility-based agent: capability has a price ceiling)
MAX_STEPS = int(os.getenv("SOUL_MAX_STEPS", "8"))
MAX_RETRIES = 3
TOOL_TIMEOUT = 30          # seconds per tool call
MAX_OBS_CHARS = 1500       # truncate observations to protect context

# Tools that stop and ask before acting (JSM rule: refuse to decide behind your back)
CONFIRM_TOOLS = {"gmail_send", "wa_send"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
VAULT_DIR = os.path.expanduser("~/bourbon/vault")
GMAIL_SCRIPT = os.path.expanduser("~/bourbon/scripts/gmail-search.py")
WA_CLI = os.path.expanduser("~/bourbon/scripts/wa")
