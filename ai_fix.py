# ai_fix.py

import requests
import json

def get_fix_recommendations(scan_result):
    """
    Sends scan results to local Ollama (llama3) and safely parses
    multi-line or multi-chunk JSON responses.
    """

    prompt = f"""
You are a cybersecurity expert. Analyze the following scan results and generate:

- Key vulnerabilities
- Severity (High/Medium/Low)
- Root causes
- Step-by-step remediation
- Patch recommendations
- Hardening steps

Scan Data:
{json.dumps(scan_result, indent=2)}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        raw = response.text.strip()

        # If Ollama returns ONE clean JSON → try direct parse
        try:
            data = json.loads(raw)
            return data.get("response", "No AI response.")
        except:
            pass  # Continue to fallback parsing

        # Fallback: Handle multi-line JSON chunks
        lines = raw.splitlines()
        final_text = ""

        for line in lines:
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        final_text += obj["response"] + "\n"
                except:
                    continue

        if final_text.strip() == "":
            return "AI did not return usable text."

        return final_text.strip()

    except Exception as e:
        print("AI error:", e)
        return "AI analysis failed. Ensure Ollama is running and llama3 is installed."
