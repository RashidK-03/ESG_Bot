import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=api_key)


def generate_summary(title: str, description: str) -> str:
    if not title:
        title = "(no title provided)"
    if not description:
        description = "(no description provided)"

    prompt = f"""You are an ESG regulatory analyst. Summarize the following update concisely.

Reply strictly in this format (plain text, no markdown, no asterisks, no headers):

🔎 What happened: [1-2 sentences]
👥 Who is affected: [1 sentence]
📌 Key points: [2-3 bullet points using • symbol]
⚡ Potential impact: [1-2 sentences]

Title: {title}
Content: {description}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"[Summary unavailable: {e}]"