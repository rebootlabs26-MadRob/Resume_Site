import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import atexit

# Load .env file from script directory
_script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_script_dir, ".env"))

# Session tracking
_session_start = datetime.now()
_session_id = _session_start.strftime("%Y%m%d_%H%M%S")

# --- SDK clients ---
# Anthropic (Claude)
from anthropic import Anthropic
# Google Generative AI (Gemini) - Updated to new library
try:
    from google import genai
    GEMINI_NEW_SDK = True
except ImportError:
    import google.generativeai as genai
    GEMINI_NEW_SDK = False
# OpenAI (GPT)
import openai

# --- Color Configuration ---
class C:
    """ANSI color codes for terminal output"""
    # Labels (bright)
    L_CLAUDE = '\033[38;5;208m'      # Orange
    L_GEMINI = '\033[38;5;129m'      # Joker Purple
    L_OPENAI = '\033[38;5;21m'       # Royal Blue
    L_JUDGE = '\033[92m'             # Green
    L_SYSTEM = '\033[91m'            # Red
    
    # Text responses (lighter shades)
    T_CLAUDE = '\033[38;5;214m'      # Light Orange
    T_GEMINI = '\033[38;5;141m'      # Light Purple
    T_OPENAI = '\033[38;5;39m'       # Light Blue
    T_JUDGE = '\033[38;5;120m'       # Light Green
    
    # User
    USER = '\033[97m'                # White
    
    # Reset
    RESET = '\033[0m'

def cprint(label_color, text_color, label, text):
    """Print colored output: label in one color, text in another"""
    print(f"{label_color}{label}:{C.RESET} {text_color}{text}{C.RESET}")

# Track if we've shown Gemini error already
_gemini_error_shown = False

# --- Configuration ---
# Use absolute path for log file to avoid directory issues
import os
_script_dir = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(_script_dir, "AIEnv_chatlog.json")
LOG_FILE = LOG_PATH  # Alias for compatibility
_session_backup = None  # Store last cleared session for undo

# Use the Claude model IDs your account supports (from client.models.list())
# You shared these:
# - claude-opus-4-5-20251101
# - claude-sonnet-4-5-20250929
# - claude-haiku-4-5-20251001
CLAUDE_MODEL_DEFAULT = os.getenv("CLAUDE_MODEL_ID", "claude-sonnet-4-5-20250929")
CLAUDE_JUDGE_MODEL = os.getenv("CLAUDE_JUDGE_MODEL_ID", "claude-opus-4-5-20251101")  # stronger judge

# Gemini model (use current v1 models)
GEMINI_MODEL = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash")

# OpenAI model
OPENAI_MODEL = os.getenv("OPENAI_MODEL_ID", "gpt-4o")

# --- API keys ---
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Guards ---
def require_keys():
    # Re-read env vars at call-time so changes during a session are respected
    global CLAUDE_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    missing = []
    if not CLAUDE_API_KEY:
        missing.append("CLAUDE_API_KEY")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}. Set them with setx and restart shell."
        )

# --- Initialize clients ---
def init_clients():
    require_keys()
    claude_client = Anthropic(api_key=CLAUDE_API_KEY)
    if not GEMINI_NEW_SDK:
        genai.configure(api_key=GEMINI_API_KEY)
    openai.api_key = OPENAI_API_KEY
    return claude_client

# --- Logging ---
def ensure_log():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump({"sessions": []}, f, ensure_ascii=False, indent=2)


def load_log():
    ensure_log()
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_session_entry(entry):
    data = load_log()
    data["sessions"].append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_history_text(max_chars=1000):
    """
    Provide condensed history as text context for 'see each other's logs' features.
    """
    data = load_log()
    chunks = []
    for s in data.get("sessions", []):
        ts = s.get("timestamp", "?")
        user = s.get("user_prompt", "")
        chunks.append(f"[{ts}] User: {user}")
        for agent in ("Claude", "Gemini", "OpenAI"):
            if agent in s.get("responses", {}):
                chunks.append(f"{agent}: {s['responses'][agent]}")
        if "judge" in s:
            chunks.append(
                f"Judge: {s['judge'].get('judge_agent', '')} -> {s['judge'].get('best_agent', '')}"
            )
            chunks.append(f"Best Outcome: {s['judge'].get('best_text', '')}")
    text = "\n".join(chunks)
    return text[-max_chars:] if len(text) > max_chars else text

# --- AI ask functions ---
def ask_claude(claude_client, prompt, model_id=None, max_tokens=400):
    model_id = model_id or CLAUDE_MODEL_DEFAULT
    try:
        msg = claude_client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        # Claude returns content as a list of blocks; use the first text block.
        if getattr(msg, "content", None) and len(msg.content) > 0 and hasattr(msg.content[0], "text"):
            return msg.content[0].text
        return str(msg)
    except Exception as e:
        return f"[ERROR] Claude call failed: {e}"


def ask_gemini(prompt, model_id=None):
    global _gemini_error_shown
    model_id = model_id or GEMINI_MODEL
    
    # Add strict system instruction for concise responses
    enhanced_prompt = (
        "CRITICAL: Respond in 2-4 concise paragraphs maximum. No bullet lists unless absolutely necessary. "
        "Be as brief and direct as Claude or ChatGPT. Get to the core answer immediately.\n\n"
        f"{prompt}"
    )
    
    try:
        if GEMINI_NEW_SDK:
            client = genai.Client(api_key=GEMINI_API_KEY)
            resp = client.models.generate_content(model=model_id, contents=enhanced_prompt)
            return resp.text if hasattr(resp, 'text') else str(resp)
        else:
            model = genai.GenerativeModel(model_id)
            resp = model.generate_content(enhanced_prompt)
            return getattr(resp, "text", "") or ""
    except Exception as e:
        error_msg = str(e)
        # Only show detailed error once
        if not _gemini_error_shown:
            _gemini_error_shown = True
            if "429" in error_msg or "quota" in error_msg.lower():
                return "[Gemini quota limit reached - consider upgrading API key or wait 24hrs]"
            return f"[Gemini error: {error_msg}]"
        else:
            return "[Gemini unavailable]"


def ask_openai(prompt, model_id=None):
    model_id = model_id or OPENAI_MODEL
    try:
        resp = openai.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
        )
        # Defensive access
        if getattr(resp, "choices", None) and len(resp.choices) > 0:
            choice = resp.choices[0]
            if getattr(choice, "message", None) and getattr(choice.message, "content", None):
                return choice.message.content
        return str(resp)
    except Exception as e:
        return f"[ERROR] OpenAI call failed: {e}"

# --- Judging ---
def judge_best_with_claude(claude_client, answers):
    """
    answers: dict { "Claude": str, "Gemini": str, "OpenAI": str }
    Returns dict with judge_agent, best_agent, best_text, rationale.
    """
    # Provide prior history for context
    history = read_history_text()
    comparison_prompt = (
        "You are the lead judge. Compare the following three answers and select the single best outcome. "
        "Prioritize factual accuracy, clarity, completeness, and actionable detail. Explain your choice briefly.\n\n"
        f"Prior conversation context:\n{history}\n\n"
        "Answers to compare:\n"
        f"- Claude: {answers.get('Claude', '')}\n"
        f"- Gemini: {answers.get('Gemini', '')}\n"
        f"- OpenAI: {answers.get('OpenAI', '')}\n\n"
        "Return your response in this strict JSON format:\n"
        '{ "best_agent": "Claude|Gemini|OpenAI", "best_text": "...", "rationale": "..." }'
    )
    judge_text = ask_claude(claude_client, comparison_prompt, model_id=CLAUDE_JUDGE_MODEL, max_tokens=500)
    # Attempt to parse the JSON (be resilient to extra text)
    parsed = {
        "best_agent": "Claude",
        "best_text": answers.get("Claude", ""),
        "rationale": "Fallback: JSON parse failed.",
    }
    try:
        start = judge_text.find("{")
        end = judge_text.rfind("}")
        if start != -1 and end != -1:
            json_str = judge_text[start : end + 1]
            parsed = json.loads(json_str)
            # Validate required keys
            if "best_agent" not in parsed or parsed["best_agent"] not in ["Claude", "Gemini", "OpenAI"]:
                parsed["best_agent"] = "Claude"
            if "best_text" not in parsed:
                parsed["best_text"] = answers.get(parsed["best_agent"], "")
            if "rationale" not in parsed:
                parsed["rationale"] = "No rationale provided"
        else:
            # No JSON found, use fallback
            parsed["rationale"] = f"Fallback: No JSON in response. Raw: {judge_text[:100]}..."
    except json.JSONDecodeError as e:
        parsed["rationale"] = f"Fallback: JSON error at position {e.pos}. Raw: {judge_text[:100]}..."
    except Exception as e:
        parsed["rationale"] = f"Fallback: {str(e)[:100]}"
        pass
    
    best_agent = parsed.get("best_agent", "Claude")
    return {
        "judge_agent": f"Claude ({CLAUDE_JUDGE_MODEL})",
        "best_agent": best_agent,
        "best_text": parsed.get("best_text", answers.get(best_agent, "")),
        "rationale": parsed.get("rationale", "No rationale provided"),
    }

# --- Session orchestration ---
def run_all_three_and_judge(claude_client, user_prompt):
    # Direct prompt without history for speed
    routed_prompt = user_prompt

    c = ask_claude(claude_client, routed_prompt)
    # small delay to avoid rate conflicts on some accounts
    time.sleep(0.2)
    g = ask_gemini(routed_prompt)
    time.sleep(0.2)
    o = ask_openai(routed_prompt)

    answers = {"Claude": c, "Gemini": g, "OpenAI": o}
    judge = judge_best_with_claude(claude_client, answers)

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_prompt": user_prompt,
        "mode": "all_three_then_judge",
        "responses": answers,
        "judge": judge,
    }
    save_session_entry(entry)
    return answers, judge


def route_single_agent(claude_client, agent, user_prompt):
    shared_context = read_history_text()
    routed_prompt = f"{shared_context}\n\nUser prompt:\n{user_prompt}"

    if agent == "claude":
        reply = ask_claude(claude_client, routed_prompt)
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_prompt": user_prompt,
            "mode": "single",
            "agent": "Claude",
            "responses": {"Claude": reply},
        }
        save_session_entry(entry)
        return reply

    elif agent == "gemini":
        reply = ask_gemini(routed_prompt)
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_prompt": user_prompt,
            "mode": "single",
            "agent": "Gemini",
            "responses": {"Gemini": reply},
        }
        save_session_entry(entry)
        return reply

    elif agent == "openai":
        reply = ask_openai(routed_prompt)
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_prompt": user_prompt,
            "mode": "single",
            "agent": "OpenAI",
            "responses": {"OpenAI": reply},
        }
        save_session_entry(entry)
        return reply

    else:
        return f"Unknown agent '{agent}'. Use claude, gemini, or openai."

# --- CLI helpers ---
MENU_TEXT = """
Menu:
  1. Talk to Claude
  2. Talk to Gemini
  3. Talk to OpenAI
  4. Run all three and judge
  5. Show last log entry
  6. Clear session (with backup)
  7. Undo last clear
  8. Exit
"""


def show_last_log():
    data = load_log()
    if not data.get("sessions"):
        print("No sessions yet.")
        return
    last = data["sessions"][-1]
    print(json.dumps(last, indent=2, ensure_ascii=False))


def parse_command(line):
    """
    Supports command-based routing:
      - 'Claude: your prompt'
      - 'Gemini: your prompt'
      - 'OpenAI: your prompt'
      - 'All: your prompt'  (runs all three + judge)
      - 'menu' (shows menu)
      - 'exit' (quit)
      - 'clear' (clear session with backup)
      - 'undo' (restore last cleared session)
    Returns (mode, agent, prompt) or ('menu', None, None), ('exit', None, None)
    """
    s = line.strip()
    if not s:
        return None, None, None
    sl = s.lower()
    if sl == "menu":
        return "menu", None, None
    if sl == "exit":
        return "exit", None, None
    if sl == "clear":
        clear_session()
        return None, None, None
    if sl == "undo":
        undo_clear()
        return None, None, None
    # Save command
    if sl.startswith("save:"):
        session_name = s.split(":", 1)[1].strip() if ":" in s and len(s.split(":", 1)) > 1 else None
        save_session(session_name)
        return None, None, None
    # All three
    if sl.startswith("all:"):
        return "all", None, s.split(":", 1)[1].strip()
    # Single agent (case-insensitive)
    for agent in ("claude", "gemini", "openai"):
        if sl.startswith(agent + ":"):
            return "single", agent, s.split(":", 1)[1].strip()
    # Default: treat as "All"
    return "all", None, s


def get_session_duration():
    """Return formatted session duration."""
    elapsed = datetime.now() - _session_start
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def get_last_topics(count=3):
    """Extract last N topics from chat log."""
    try:
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data or "entries" not in data:
            return []
        recent = data["entries"][-count:]
        topics = []
        for entry in recent:
            user_prompt = entry.get("user_prompt", "")[:60]
            if len(entry.get("user_prompt", "")) > 60:
                user_prompt += "..."
            topics.append(user_prompt)
        return topics
    except:
        return []


def clear_session():
    """Clear current session history (with backup for undo)."""
    global _session_backup
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                _session_backup = json.load(f)
            
            # Clear the log file
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump({"sessions": []}, f, ensure_ascii=False, indent=2)
            
            print(f"{C.L_SYSTEM}✓ Session cleared. Type 'undo' to restore.{C.RESET}")
            return True
    except Exception as e:
        print(f"{C.L_SYSTEM}✗ Failed to clear session: {e}{C.RESET}")
    return False


def undo_clear():
    """Restore last cleared session."""
    global _session_backup
    if _session_backup is None:
        print(f"{C.L_SYSTEM}✗ No cleared session to restore.{C.RESET}")
        return False
    
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(_session_backup, f, ensure_ascii=False, indent=2)
        
        entry_count = len(_session_backup.get("sessions", []))
        print(f"{C.L_SYSTEM}✓ Restored {entry_count} messages from backup.{C.RESET}")
        _session_backup = None
        return True
    except Exception as e:
        print(f"{C.L_SYSTEM}✗ Failed to restore session: {e}{C.RESET}")
    return False


def save_session(name=None):
    """Save current session with optional name."""
    session_name = name if name else _session_id
    session_dir = os.path.join(_script_dir, "sessions")
    os.makedirs(session_dir, exist_ok=True)
    
    session_file = os.path.join(session_dir, f"{session_name}.json")
    
    # Copy current log to session file
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["session_name"] = session_name
            data["session_duration"] = get_session_duration()
            data["saved_at"] = datetime.now().isoformat()
            
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"{C.L_SYSTEM}✓ Session saved: {session_name}{C.RESET}")
            return True
    except Exception as e:
        print(f"{C.L_SYSTEM}✗ Failed to save session: {e}{C.RESET}")
    return False


def run_cli():
    claude_client = init_clients()
    ensure_log()
    
    # Show session header
    print(f"\n{C.L_SYSTEM}{'='*60}{C.RESET}")
    print(f"{C.L_SYSTEM}Multi‑AI Chat (Claude/Gemini/OpenAI){C.RESET}")
    print(f"{C.L_SYSTEM}Session: {_session_id}{C.RESET}")
    
    # Show last topics if available
    topics = get_last_topics(3)
    if topics:
        print(f"{C.L_SYSTEM}\nLast session topics:{C.RESET}")
        for i, topic in enumerate(topics, 1):
            print(f"{C.L_SYSTEM}  {i}. {topic}{C.RESET}")
    
    print(f"{C.L_SYSTEM}{'='*60}{C.RESET}")
    print(f"{C.L_SYSTEM}Commands: 'menu' | 'save:name' | 'clear' | 'undo' | 'exit'{C.RESET}")
    print(f"{C.L_SYSTEM}Examples: 'Claude: analyze config.txt', 'All: summarize today's logs'{C.RESET}")

    while True:
        session_time = get_session_duration()
        user_input = input(f"\n{C.L_SYSTEM}[{session_time}] You:{C.RESET} {C.USER}")
        line = user_input.strip()
        print(C.RESET, end='')  # Reset color after input
        mode, agent, prompt = parse_command(line)
        if mode is None:
            continue
        if mode == "exit":
            # Exit warning with save prompt
            save_choice = input(f"{C.L_SYSTEM}Save current session before exiting? (y/n):{C.RESET} {C.USER}").strip().lower()
            print(C.RESET, end='')
            if save_choice == 'y':
                session_name = input(f"{C.L_SYSTEM}Session name (leave blank for auto):{C.RESET} {C.USER}").strip()
                print(C.RESET, end='')
                save_session(session_name if session_name else None)
            print(f"{C.L_SYSTEM}Goodbye. Session duration: {session_time}{C.RESET}")
            break
        if mode == "menu":
            print(MENU_TEXT)
            choice = input("Select: ").strip()
            if choice == "1":
                user_prompt = input(f"{C.L_SYSTEM}Prompt for Claude:{C.RESET} {C.USER}")
                print(C.RESET, end='')
                reply = route_single_agent(claude_client, "claude", user_prompt)
                cprint(C.L_CLAUDE, C.T_CLAUDE, "\nClaude", reply)
            elif choice == "2":
                user_prompt = input(f"{C.L_SYSTEM}Prompt for Gemini:{C.RESET} {C.USER}")
                print(C.RESET, end='')
                reply = route_single_agent(claude_client, "gemini", user_prompt)
                cprint(C.L_GEMINI, C.T_GEMINI, "\nGemini", reply)
            elif choice == "3":
                user_prompt = input(f"{C.L_SYSTEM}Prompt for OpenAI:{C.RESET} {C.USER}")
                print(C.RESET, end='')
                reply = route_single_agent(claude_client, "openai", user_prompt)
                cprint(C.L_OPENAI, C.T_OPENAI, "\nOpenAI", reply)
            elif choice == "4":
                user_prompt = input(f"{C.L_SYSTEM}Prompt to run across all three:{C.RESET} {C.USER}")
                print(C.RESET, end='')
                answers, judge = run_all_three_and_judge(claude_client, user_prompt)
                cprint(C.L_CLAUDE, C.T_CLAUDE, "\nClaude", answers["Claude"])
                cprint(C.L_GEMINI, C.T_GEMINI, "\nGemini", answers["Gemini"])
                cprint(C.L_OPENAI, C.T_OPENAI, "\nOpenAI", answers["OpenAI"])
                cprint(C.L_JUDGE, C.T_JUDGE, f"\nJudge: [{judge['best_agent']}]", judge["rationale"])
            elif choice == "5":
                show_last_log()
            elif choice == "6":
                clear_session()
            elif choice == "7":
                undo_clear()
            elif choice == "8":
                print(f"{C.L_SYSTEM}Goodbye.{C.RESET}")
                break
            else:
                print("Invalid choice.")
            continue

        # Command-based paths
        if mode == "single":
            reply = route_single_agent(claude_client, agent, prompt)
            if agent == "claude":
                cprint(C.L_CLAUDE, C.T_CLAUDE, "\nClaude", reply)
            elif agent == "gemini":
                cprint(C.L_GEMINI, C.T_GEMINI, "\nGemini", reply)
            elif agent == "openai":
                cprint(C.L_OPENAI, C.T_OPENAI, "\nOpenAI", reply)

        elif mode == "all":
            answers, judge = run_all_three_and_judge(claude_client, prompt)
            cprint(C.L_CLAUDE, C.T_CLAUDE, "\nClaude", answers["Claude"])
            cprint(C.L_GEMINI, C.T_GEMINI, "\nGemini", answers["Gemini"])
            cprint(C.L_OPENAI, C.T_OPENAI, "\nOpenAI", answers["OpenAI"])
            cprint(C.L_JUDGE, C.T_JUDGE, f"\nJudge: [{judge['best_agent']}]", judge["rationale"])


if __name__ == "__main__":
    run_cli()
