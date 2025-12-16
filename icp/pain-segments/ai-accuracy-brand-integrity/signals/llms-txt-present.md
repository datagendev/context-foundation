# Signal: `llms.txt` present (or linked) on their site

## What it indicates
They’re taking explicit steps to influence how AI systems interpret their site.
This is usually an **awareness / “they care”** signal, not proof of pain.

## How to detect (programmatic)
- Fetch `https://{domain}/llms.txt`
  - Score higher if response is `200`, content is Markdown, and it links to canonical docs/pricing/security pages.
- Optional: also crawl the docs subdomain and look for `llms.txt` linked in the footer/navigation.

## Output fields (recommended)
- `llms_txt_found` (bool)
- `llms_txt_url` (string)
- `llms_txt_links_count` (int)
- `llms_txt_mentions_pricing_security_compliance` (bool)

## Caveats / false positives
- It’s an emerging convention; presence may indicate experimentation rather than urgency.
- Some sites host it on docs subdomains or in non-root paths; a root-only check will miss those.

