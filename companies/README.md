# Companies

This folder stores **company-specific research and artifacts** (one subfolder per company), so TAM inputs, web research outputs, and notes live next to each other.

## Structure

Use the company’s primary domain as the folder name:

```
companies/
  scrunch.com/
    README.md
    site-map/
      2025-12-14.json
      2025-12-14.md
    pages/
      enterprise__<id>.md
      pricing__<id>.md
```

## Conventions

- Folder name: the canonical website host (e.g. `scrunch.com`, `acme.io`).
- Keep files small and link to sources when possible.
- Put generated outputs under a clear subfolder (e.g. `site-map/`, `research/`, `assets/`).
