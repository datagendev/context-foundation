#!/usr/bin/env python3
"""
Automated Competitive Research Workflow

Automates the process of researching a competitor using OpenAI deep research
and creating the necessary folder structure and files.

Examples:
  # Quick reconnaissance (5-10 min)
  uv run python integration/research-competitor.py \
    --domain peec.ai \
    --company-name "Peec.ai" \
    --depth quick

  # Standard research (20-30 min, default)
  uv run python integration/research-competitor.py \
    --domain brightedge.com \
    --company-name "BrightEdge"

  # Focused research on specific areas
  uv run python integration/research-competitor.py \
    --domain otterly.ai \
    --company-name "Otterly.AI" \
    --research-focus product,customers,positioning \
    --skip-scraping

  # Comprehensive analysis with custom queries (1-2 hrs)
  uv run python integration/research-competitor.py \
    --domain conductor.com \
    --company-name "Conductor" \
    --depth comprehensive \
    --comparison-context "Scrunch and other AI SEO platforms" \
    --custom-queries "What is their enterprise pricing model?" \
    --custom-queries "Which Fortune 500 companies use Conductor?"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_command(cmd: list[str], description: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, check=False, capture_output=False, text=True)

    if check and result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        sys.exit(1)

    print(f"\n✓ {description} completed")
    return result


def create_folder_structure(domain: str) -> Path:
    """Create the base folder structure for a competitor."""
    repo_root = _repo_root()
    company_dir = repo_root / "company" / domain
    ci_dir = company_dir / "competitive-intelligence"
    research_dir = ci_dir / "research"
    analysis_dir = ci_dir / "analysis"

    # Create directories
    research_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n✓ Created folder structure at: {company_dir}")
    print(f"  - {ci_dir}")
    print(f"  - {research_dir}")
    print(f"  - {analysis_dir}")

    return company_dir


def create_base_readme(company_dir: Path, domain: str, company_name: str, category: str) -> None:
    """Create base README for the competitor."""
    readme_path = company_dir / "README.md"

    if readme_path.exists():
        print(f"\n⚠️  README already exists at {readme_path}, skipping...")
        return

    content = f"""# {company_name}

- **Website:** https://{domain}
- **Category:** {category}
- **Status:** Competitor in AI search optimization

## Overview

{company_name} is a competitor in the AI search optimization space.

## Contents

- `competitive-intelligence/`: Competitive analysis and research
  - `profile.md`: Synthesized competitive profile
  - `research/`: Deep research outputs (product, customers, positioning)
  - `analysis/`: Manual analysis notes
- `site-map/`: URL inventory (if website mapping performed)
- `pages/`: Scraped website pages (if applicable)

## Research Status

- **Last Updated:** {datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")}
- **Research Phase:** Initial
- **Profile Completeness:** Pending

## Next Actions

- [ ] Complete deep research queries
- [ ] Scrape key website pages
- [ ] Fill in competitive profile
- [ ] Add to comparison matrix
"""

    _safe_write(readme_path, content)
    print(f"\n✓ Created README at: {readme_path}")


def run_deep_research_queries(
    domain: str,
    company_name: str,
    research_dir: Path,
    model: str = "o3-deep-research-2025-06-26",
    research_focus: str = "all",
    depth: str = "standard",
    comparison_context: str = "Scrunch",
    custom_queries: list[str] | None = None,
) -> list[str]:
    """Run deep research queries for the competitor based on focus and depth."""
    repo_root = _repo_root()
    script_path = repo_root / "integration" / "openai-deep-research.py"

    # Define all possible research queries
    all_queries = {
        "product": (
            "product-analysis",
            f"What products and features does {company_name} offer for AI search optimization? "
            f"Include pricing tiers, core capabilities, and key differentiators compared to "
            f"{comparison_context} and competitors in AI SEO/LLM visibility space. How do they help "
            f"brands appear in ChatGPT, Perplexity, and other AI platforms?"
        ),
        "customers": (
            "customer-segments",
            f"Who are {company_name}'s customers? What customer segments do they target? "
            f"Include case studies, testimonials, and examples of companies using their "
            f"AI search optimization platform. What industries and company sizes do they serve?"
        ),
        "positioning": (
            "market-positioning",
            f"How does {company_name} position itself in the AI search optimization market? "
            f"What is their messaging strategy, value proposition, and competitive differentiation "
            f"compared to {comparison_context}? What do they emphasize in their marketing and sales materials?"
        ),
        "technology": (
            "technology-stack",
            f"What is {company_name}'s technology stack, product architecture, and technical approach? "
            f"What technologies power their platform? What are their recent product launches and "
            f"roadmap signals based on job postings, engineering blog posts, or announcements?"
        ),
        "team": (
            "team-company",
            f"Who are the key leaders and team members at {company_name}? What is the company's "
            f"funding history, investors, and recent news? What is their company culture and hiring strategy?"
        ),
    }

    # Determine which queries to run based on focus and depth
    queries = []

    if depth == "quick":
        # Quick: single broad query combining all aspects
        queries.append((
            "overview",
            f"Provide a comprehensive overview of {company_name} as an AI search optimization competitor. "
            f"Cover: (1) core products and pricing, (2) target customers and notable brands, "
            f"(3) market positioning and differentiation compared to {comparison_context}. "
            f"Include specific examples, case studies, and quantifiable data where available."
        ))
    elif depth == "comprehensive":
        # Comprehensive: all queries
        if research_focus == "all":
            queries.extend(list(all_queries.values()))
        else:
            focus_areas = [f.strip() for f in research_focus.split(",")]
            for area in focus_areas:
                if area in all_queries:
                    queries.append(all_queries[area])
    else:  # standard
        # Standard: product, customers, positioning (original 3)
        if research_focus == "all":
            queries.extend([all_queries["product"], all_queries["customers"], all_queries["positioning"]])
        else:
            focus_areas = [f.strip() for f in research_focus.split(",")]
            for area in focus_areas:
                if area in all_queries:
                    queries.append(all_queries[area])

    # Add custom queries if provided
    if custom_queries:
        for i, custom_query in enumerate(custom_queries, 1):
            queries.append((f"custom-query-{i}", custom_query))

    response_ids = []

    for query_name, query_text in queries:
        print(f"\n{'='*60}")
        print(f"Running deep research query: {query_name}")
        print(f"{'='*60}")

        # Run the query
        cmd = [
            "uv", "run", "python",
            str(script_path),
            "--query", query_text,
            "--model", model,
            "--output-dir", str(research_dir),
        ]

        result = run_command(
            cmd,
            f"Deep Research: {query_name}",
            check=True
        )

        # Note: response IDs would be in the output, but for simplicity we'll just track success
        print(f"\n✓ Completed research query: {query_name}")

    return response_ids


def create_profile_placeholder(ci_dir: Path, company_name: str) -> None:
    """Create a placeholder profile from the template."""
    repo_root = _repo_root()
    template_path = repo_root / "company" / ".templates" / "competitive-intelligence" / "profile-template.md"
    profile_path = ci_dir / "profile.md"

    if profile_path.exists():
        print(f"\n⚠️  Profile already exists at {profile_path}, skipping...")
        return

    if not template_path.exists():
        print(f"\n⚠️  Template not found at {template_path}, creating basic profile...")
        content = f"""# {company_name} - Competitive Intelligence

**Last Updated:** {datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")}
**Research Status:** Initial

## TODO

Review deep research outputs in `research/` folder and fill in this profile using the template at:
`company/.templates/competitive-intelligence/profile-template.md`

## Research Sources

- Deep research outputs in `./research/`
- Scraped pages in `../pages/` (if applicable)
"""
    else:
        # Copy template
        content = template_path.read_text(encoding="utf-8")
        # Could do replacements here, but leaving as-is for manual filling

    _safe_write(profile_path, content)
    print(f"\n✓ Created profile placeholder at: {profile_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated competitive research workflow for a competitor."
    )
    parser.add_argument(
        "--domain",
        type=str,
        required=True,
        help="Competitor domain (e.g., brightedge.com)",
    )
    parser.add_argument(
        "--company-name",
        type=str,
        required=True,
        help="Company name (e.g., 'BrightEdge')",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="AI Search Optimization Platform",
        help="Category/industry (default: AI Search Optimization Platform)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="o3-deep-research-2025-06-26",
        help="Deep research model (default: o3-deep-research-2025-06-26, alternative: o4-mini-deep-research-2025-06-26)",
    )
    parser.add_argument(
        "--research-focus",
        type=str,
        default="all",
        help="Research focus areas: product,customers,positioning,technology,team or 'all' (default: all)",
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Research depth: quick (5-10min), standard (20-30min), comprehensive (1-2hrs) (default: standard)",
    )
    parser.add_argument(
        "--comparison-context",
        type=str,
        default="Scrunch",
        help="Who to compare against in research queries (default: Scrunch)",
    )
    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip website scraping step",
    )
    parser.add_argument(
        "--skip-profile",
        action="store_true",
        help="Skip creating profile placeholder",
    )
    parser.add_argument(
        "--update-matrix",
        action="store_true",
        default=False,
        help="Prompt to update comparison matrix after research (default: false)",
    )
    parser.add_argument(
        "--custom-queries",
        type=str,
        action="append",
        help="Additional custom research queries (can be specified multiple times)",
    )
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"Automated Competitive Research: {args.company_name}")
    print(f"{'='*60}")
    print(f"Domain: {args.domain}")
    print(f"Category: {args.category}")
    print(f"Research Focus: {args.research_focus}")
    print(f"Depth: {args.depth}")
    print(f"Comparison Context: {args.comparison_context}")
    print(f"Model: {args.model}")
    print(f"Skip Scraping: {args.skip_scraping}")
    print(f"Skip Profile: {args.skip_profile}")
    print(f"Update Matrix: {args.update_matrix}")
    if args.custom_queries:
        print(f"Custom Queries: {len(args.custom_queries)} additional queries")

    # Step 1: Create folder structure
    print(f"\n{'='*60}")
    print("STEP 1: Creating folder structure")
    print(f"{'='*60}")
    company_dir = create_folder_structure(args.domain)
    ci_dir = company_dir / "competitive-intelligence"
    research_dir = ci_dir / "research"

    # Step 2: Create base README
    print(f"\n{'='*60}")
    print("STEP 2: Creating base README")
    print(f"{'='*60}")
    create_base_readme(company_dir, args.domain, args.company_name, args.category)

    # Step 3: Run deep research queries
    depth_time_estimates = {
        "quick": "5-10 minutes",
        "standard": "20-30 minutes",
        "comprehensive": "1-2 hours"
    }
    estimated_time = depth_time_estimates.get(args.depth, "20-30 minutes")

    print(f"\n{'='*60}")
    print(f"STEP 3: Running deep research queries (estimated: {estimated_time})")
    print(f"{'='*60}")
    try:
        run_deep_research_queries(
            args.domain,
            args.company_name,
            research_dir,
            args.model,
            args.research_focus,
            args.depth,
            args.comparison_context,
            args.custom_queries,
        )
    except Exception as e:
        print(f"\n❌ Deep research failed: {e}")
        print("\nYou can run the queries manually:")
        print(f"  uv run python integration/openai-deep-research.py --query \"...\" --output-dir {research_dir}")
        return 1

    # Step 4: Create profile placeholder (optional)
    if not args.skip_profile:
        print(f"\n{'='*60}")
        print("STEP 4: Creating profile placeholder")
        print(f"{'='*60}")
        create_profile_placeholder(ci_dir, args.company_name)

    # Step 5: Summary and next steps
    print(f"\n{'='*60}")
    print("✅ RESEARCH WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"\nCompetitor folder created at: {company_dir}")
    print(f"\nResearch Configuration:")
    print(f"  - Depth: {args.depth} ({estimated_time})")
    print(f"  - Focus: {args.research_focus}")
    print(f"  - Comparison Context: {args.comparison_context}")
    print(f"\nNext steps:")
    print(f"  1. Review research outputs in: {research_dir}")
    print(f"  2. Fill in competitive profile: {ci_dir / 'profile.md'}")
    if args.update_matrix:
        print(f"  3. Update comparison matrix: company/competitive-landscape/comparison-matrix.md")
        print(f"  4. Update landscape README: company/competitive-landscape/README.md")
    else:
        print(f"  3. (Optional) Update comparison matrix: company/competitive-landscape/comparison-matrix.md")
        print(f"  4. (Optional) Update landscape README: company/competitive-landscape/README.md")

    if not args.skip_scraping:
        print(f"\nOptional: Scrape key website pages:")
        print(f"  uv run python integration/company-scrape-url.py \\")
        print(f"    --url https://{args.domain}/product \\")
        print(f"    --url https://{args.domain}/pricing \\")
        print(f"    --only-main-content")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
