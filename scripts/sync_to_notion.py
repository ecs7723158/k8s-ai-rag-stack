#!/usr/bin/env python3
"""
Notion Knowledge Base Automation Sync Script
Author: @ecs7723158
Synchronizes markdown documentation directly to Notion pages via the official Notion REST API.
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error

NOTION_API_VERSION = "2022-06-28"
NOTION_ENDPOINT = "https://api.notion.com/v1/blocks/{block_id}/children"

def markdown_to_notion_blocks(markdown_text: str):
    """
    Parses Markdown text into Notion Block JSON structures.
    Supports headings, bullet lists, code blocks, callouts, and paragraphs.
    """
    lines = markdown_text.splitlines()
    blocks = []
    in_code_block = False
    code_lang = "plain text"
    code_buffer = []

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lang = stripped[3:].strip() or "plain text"
                # Map common markdown languages to Notion accepted languages
                lang_map = {"python": "python", "py": "python", "go": "go", "yaml": "yaml", "yml": "yaml", "bash": "bash", "sh": "bash", "json": "json"}
                code_lang = lang_map.get(code_lang.lower(), "plain text")
                code_buffer = []
            else:
                in_code_block = False
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buffer)}}],
                        "language": code_lang
                    }
                })
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Ignore empty lines
        if not stripped:
            continue

        # Heading 1
        if stripped.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                }
            })
        # Heading 2
        elif stripped.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[3:]}}]
                }
            })
        # Heading 3
        elif stripped.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[4:]}}]
                }
            })
        # Callout / Blockquote
        elif stripped.startswith("> "):
            callout_text = stripped[2:]
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": callout_text}}],
                    "icon": {"emoji": "💡"}
                }
            })
        # Bullet list item
        elif stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": stripped[2:]}}]
                }
            })
        # Default Paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": stripped}}]
                }
            })

    return blocks

def sync_blocks_to_notion(blocks, token: str, page_id: str, dry_run: bool = False):
    """
    Sends block data in batches (max 100 per Notion API call) to the specified Notion page.
    """
    # Clean page_id if formatted with dashes or raw UUID
    cleaned_page_id = page_id.replace("-", "")
    url = NOTION_ENDPOINT.format(block_id=cleaned_page_id)

    print(f"[*] Total parsed Notion blocks: {len(blocks)}")
    if dry_run:
        print("[*] DRY RUN ACTIVE: Validation passed. Sample block payload:")
        print(json.dumps(blocks[:3], indent=2, ensure_ascii=False))
        return True

    batch_size = 50
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION
    }

    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        payload = json.dumps({"children": batch}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")

        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status in (200, 201):
                    print(f"[✓] Successfully appended batch {i//batch_size + 1}/{(len(blocks)-1)//batch_size + 1}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            print(f"[!] Notion API Error: HTTP {e.code} - {err_body}", file=sys.stderr)
            return False

    print("[🎉] All documentation successfully synchronized to Notion!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Sync Markdown docs to Notion")
    parser.add_argument("--token", default=os.getenv("NOTION_API_KEY", ""), help="Notion Internal Integration Token")
    parser.add_argument("--page-id", default=os.getenv("NOTION_PAGE_ID", ""), help="Target Notion Page UUID")
    parser.add_argument("--file", default="docs/TOP5_AI_K8S_RAG_PLAYBOOK.md", help="Markdown file to sync")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print blocks without calling Notion API")
    args = parser.parse_args()

    # Determine file path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, args.file)
    if not os.path.exists(target_path):
        target_path = args.file

    if not os.path.exists(target_path):
        print(f"[!] File not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = markdown_to_notion_blocks(content)

    if not args.dry_run and (not args.token or not args.page_id):
        print("[!] No Notion Token or Page ID provided.")
        print("[*] Performing validation DRY-RUN automatically...")
        args.dry_run = True

    success = sync_blocks_to_notion(blocks, args.token, args.page_id, dry_run=args.dry_run)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
