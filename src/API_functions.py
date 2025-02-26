from groq import Groq
import anthropic

import os
import sys
import re

from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig
import asyncio
from functools import wraps

from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

client_claude = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

SYSTEM_PROMPT = """
あなたは優秀なAIアシスタントです。
"""

def claude_chat(
    user_inputs, system_prompt=SYSTEM_PROMPT, main_model="claude-3-5-haiku-20241022"
):
    completion = client_claude.messages.create(
        model=main_model,
        system=system_prompt,
        max_tokens=8192,
        temperature=1,
        messages=user_inputs,
    )
    return completion.content[0].text

def extract_tag(text, output_type="text", tag_name="output"):
    if tag_name == "output":
        pattern = r"<output>(.*?)</output>"
    elif tag_name == "code":
        pattern = r"<code>(.*?)</code>"
    elif tag_name == "input":
        pattern = r"<input>(.*?)</input>"
    else:
        try:
            pattern = rf"<{tag_name}>(.*?)</{tag_name}>"
        except:
            raise ValueError(
                "Invalid tag_name. Please choose from 'output', 'code' or 'input'."
            )
    matches = re.findall(
        pattern, text, re.DOTALL
    )  # re.DOTALL allows '.' to match newline characters
    if output_type == "text":
        return matches[0]
    elif output_type == "list":
        return matches


def sync_wrapper(async_func):
    @wraps(async_func)
    def sync_func(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))
    return sync_func

@sync_wrapper
async def claude_agent(task, model_name:str="claude-3-7-sonnet-20250219"):
    # データベースから設定を取得
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    chrome_path = os.environ.get("CHROME_BROWSER_PATH")
    
    if not api_key:
        raise ValueError("APIキーが設定されていません。設定画面から設定してください。")

    try:
        browser = Browser(
            config=BrowserConfig(
                chrome_instance_path=chrome_path,
            )
        )

        agent = Agent(
            task=task,
            llm=ChatAnthropic(
                model=model_name,
                api_key=api_key,
            ),
            browser=browser
        )
        result = await agent.run()
        return result.final_result()
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"
