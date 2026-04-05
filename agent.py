import asyncio
import sys
from ddgs import DDGS
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


def search(topic: str) -> list[dict]:
    with DDGS() as ddgs:
        return list(ddgs.text(topic, max_results=3))


async def main():
    topic = input("Topic: ").strip()
    if not topic:
        sys.exit("No topic provided.")

    print(f"\nSearching DuckDuckGo for: {topic}")
    results = search(topic)

    if not results:
        sys.exit("No results found.")

    urls = [r["href"] for r in results]
    summaries = "\n".join(
        f"{i+1}. {r['title']} — {r['href']}\n   {r['body']}"
        for i, r in enumerate(results)
    )

    print(f"Found {len(urls)} results. Starting agent...\n")

    prompt = f"""Research the topic "{topic}" and write a markdown report to output.md.

Here are the top 3 search results:
{summaries}

URLs to fetch:
{chr(10).join(urls)}

Instructions:
1. Use WebFetch to read each of the 3 URLs above
2. Synthesize what you learn into a well-structured markdown report
3. Write the report to output.md with:
   - A title and introduction
   - Key findings and insights
   - A sources section listing the 3 URLs
"""

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["WebFetch", "Write"],
            permission_mode="acceptEdits",
            cwd="/Users/jimmybradford/claude-sdk-tutorial",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"\nDone: {message.subtype}")
            if message.subtype == "success":
                print("Report written to output.md")


asyncio.run(main())
