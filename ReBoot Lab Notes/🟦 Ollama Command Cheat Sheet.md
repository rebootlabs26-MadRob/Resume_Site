
Local LLM Management + Terminal Efficiency

🔹 Model Management

• `ollama list` — list installed models  
• `ollama pull` — download model  
• `ollama rm` — remove model  
• `ollama show` — show metadata

🔹 Running Models

• `ollama run` — interactive chat  
• `ollama run --prompt "` — one-shot prompt  
• `ollama run -f` — run prompt from file

🔹 Model Creation / Modding

• `ollama create -f Modelfile`  
• `ollama serve` — start Ollama server  
• `ollama pull :latest` — update

🔹 Networking / API

• `curl http://localhost:11434/api/generate -d '{ "model": "", "prompt": "`  
• `ollama ps` — list running sessions

🔹 Troubleshooting

• Model won’t run → `ollama serve`  
• Port conflict → kill process using port **11434**  
• Model corrupted → `ollama rm` then re‑pull  
• Slow performance → check GPU drivers

	To Use/Talk 
	olla "...."

