import requests
import json

def parse_with_llm(provider, api_key, dom_chunks, parse_description):
    
    # 1. Basic Setup
    headers = {"Content-Type": "application/json"}
    final_output = []
    
    # Check if chunks are empty before sending
    if not dom_chunks or all(not chunk.strip() for chunk in dom_chunks):
        return "Error: The text content to parse is empty. Please check your scraping step."

    # 2. Configure Provider
    if provider == "gemini":
        model = "gemini-2.0-flash" 
        base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    elif provider == "groq":
        headers["Authorization"] = f"Bearer {api_key}"
        base_url = "https://api.groq.com/openai/v1/chat/completions"
        model = "llama3-70b-8192"
    elif provider == "openai":
        headers["Authorization"] = f"Bearer {api_key}"
        base_url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-4o-mini"
    else:
        return "Error: Invalid provider selected."

    # 3. Processing Loop
    for i, chunk in enumerate(dom_chunks):
        if not chunk.strip():
            continue

        prompt = f"""
        Extract the following information: {parse_description}
        From this content: {chunk}
        
        If the information is NOT found, reply exactly with: "NO_DATA"
        """

        # Prepare Payload
        if provider == "gemini":
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
        else:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }

        try:
            # 4. Make Request
            resp = requests.post(base_url, json=payload, headers=headers if provider != "gemini" else None)
            
            # IF ERROR: Return the error message to the UI
            if resp.status_code != 200:
                error_msg = f"Error (Chunk {i}): API returned {resp.status_code} - {resp.text}"
                final_output.append(error_msg)
                continue

            # 5. Parse Response
            data = resp.json()
            result_text = ""

            if provider == "gemini":
                # Safety check for Gemini's specific response structure
                if "candidates" in data and data["candidates"]:
                    result_text = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    result_text = "Error: Gemini returned no candidates (Safety filter?)"
            else:
                result_text = data["choices"][0]["message"]["content"]

            # Filter out "NO_DATA" responses
            if "NO_DATA" not in result_text:
                final_output.append(result_text)

        except Exception as e:
            final_output.append(f"Critical Error: {str(e)}")

    # 6. Final Result Handling
    if not final_output:
        return "No matching data found in the content."
    
    return "\n".join(final_output)