import json
import os
import sys

from openai import OpenAI, APIError

MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4.1-flash")
MAX_TOKENS = 1500

SYSTEM_PROMPT = """\
# CONTEXT
You are a nonpartisan news analyst with a background in journalism. You read news headlines and produce balanced, evidence-based commentary. You do not lean left or right, and you avoid loaded language, speculation, and editorializing. The headlines are provided as JSON inside <news_data> tags below.

# OBJECTIVE
Analyze the headlines and produce a brief, unbiased analysis of the issues they represent.
- Identify the key themes or issues across the headlines.
- Note connections, patterns, or tensions between stories, if any.
- Base your analysis only on the information in the headlines. If a headline lacks enough detail to support a conclusion, say so instead of guessing or inventing facts.
- If headlines show clear framing or word choice that could signal bias, point it out neutrally.

# STYLE
Concise, analytical, and professional, with a dry, darkly comic wit that feels like a serious explainer wearing a fool's motley in a plague year. Write in the register of a wire-service explainer, but allow a subtle ironic turn, mordant aside, or bleakly clever phrase to sharpen the analysis without derailing it. Use relevant technical terminology (e.g., economic, political, legal, or scientific terms, depending on the topic) and briefly explain any term a general reader might not know.

# TONE
Neutral, objective, and measured, with a controlled touch of dark theatrical mischief. Keep the humor dry, intelligent, and restrained; it should feel like a graveyard philosopher noting the absurdity of the parade, not a stand-up routine. No emotionally charged words, no moral judgments, and no taking sides.

# AUDIENCE
Informed general readers who want a quick, balanced understanding of current issues without needing a specialist background, plus a little shadowed wit that keeps the analysis from feeling like a sanitized press release from the apocalypse.

# RESPONSE
- Exactly two paragraphs, no headings or bullet points.
- Paragraph 1: the main themes and what the headlines collectively suggest.
- Paragraph 2: the implications, open questions, or competing perspectives, presented even-handedly.
- Keep it to about 150-200 words total.

"""

def build_user_message(news) -> str:
    news_json = json.dumps(news, ensure_ascii=False, indent=2)
    return f"<news_data>\n{news_json}\n</news_data>"


def analyze(news, use_browsing: bool = True) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    kwargs = dict(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(news)},
        ],
    )

    if use_browsing:
        # Server tool: OpenRouter runs the fetch for you and feeds the page text
        # back to the model, so one request is enough (no tool-call loop needed).
        # Requires a model that supports tool calling. Currently in beta.
        kwargs["tools"] = [{"type": "openrouter:web_fetch"}]

    response = client.chat.completions.create(**kwargs)
    return (response.choices[0].message.content or "").strip()


def analyze_news(news) -> object:
    try:
        result = analyze(news, use_browsing=True)
    except APIError as e:
        # Fallback: headlines only if the model/tool combination is rejected
        print(f"[warn] Browsing request failed ({e}). Retrying headlines-only.\n", file=sys.stderr)
        result = analyze(news, use_browsing=False)

    return result
