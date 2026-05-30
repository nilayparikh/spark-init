# Documentation Guide

This guide explains how to contribute to the `.init` documentation site.

## Documentation Structure

The documentation is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and lives in `docs/`. The site is organized into five sections:

```
docs/
├── index.md                          # Site home
├── getting-started/                  # New user onboarding
│   ├── quickstart.md
│   └── prerequisites.md
├── architecture/                     # How the stack works
│   ├── overview.md
│   ├── inference-stack.md
│   ├── observability-stack.md
│   └── networking.md
├── configuration/                    # Reference material
│   ├── docker-compose.md
│   ├── environment-variables.md
│   └── custom-configs.md
├── guides/                           # How-to tutorials
│   ├── adding-models.md
│   ├── observability-setup.md
│   ├── gpu-configuration.md
│   └── troubleshooting.md
├── api/                              # API references
│   └── openai-compatible.md
├── reference/                        # Catalogs and lookups
│   ├── file-index.md
│   └── docker-images.md
└── contributing/                     # Contributor guides
    ├── development.md
    └── docs-guide.md
```

## Writing Style

### Headings

Use level-2 headings (`##`) for sections within a page. The page title is a level-1 heading (`#`) on the first line.

### Code Blocks

Always specify the language for syntax highlighting:

````markdown
```bash
docker compose up -d
```

```yaml
services:
  postgres:
    image: postgres:latest
```
````

### Links

- Link to other docs pages using relative paths: `[quick start](../getting-started/quickstart.md)`
- Link to external resources with full URLs: `[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)`

### Tables

Use tables for structured data (environment variables, ports, images). Keep columns narrow and wrap long descriptions:

```markdown
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `4000` | Host port for the LiteLLM proxy |
```

### Insights

At the end of guides, add a brief insight block with 2–3 key takeaways using a blockquote:

```markdown
> **★ Insight**
> - Key takeaway one.
> - Key takeaway two.
> - Key takeaway three.
```

## Navigation

The navigation tree is defined in `mkdocs.yml` under `nav:`. When adding a new page:

1. Create the markdown file in the appropriate `docs/` subdirectory
2. Add it to the `nav:` section of `mkdocs.yml` in the logical position
3. Verify it appears in the sidebar with `mkdocs serve`

## Local Preview

```bash
pip install mkdocs-material
mkdocs serve
```

The site will be available at `http://localhost:8000` with live reload on file changes.

## Building the Site

```bash
mkdocs build
```

The output lands in `site/`. This is what gets deployed to GitHub Pages.

## Common Tasks

### Adding a New Guide

1. Create `docs/guides/my-new-guide.md`
2. Add to `mkdocs.yml` under the **Guides** nav section
3. Cross-reference from related pages (e.g., link from troubleshooting if applicable)

### Updating an Existing Page

1. Edit the markdown file
2. Run `mkdocs serve` to verify formatting
3. Check that internal links still resolve

### Adding a Dashboard

New Grafana dashboards go in `observability/config/grafana/provisioning/dashboards/machine/`. Document them in `docs/guides/observability-setup.md` under the "Available Dashboards" table.

## What Not to Document

- **Machine-specific configuration**: Hostnames, IP addresses, and local paths belong in `.env.example` with comments, not in docs.
- **Third-party internals**: Don't document llama.cpp source code; link to the upstream repository instead.
- **Transient workarounds**: If a fix is a one-time workaround for a specific bug, document it in the issue tracker, not the docs.

> **★ Insight**
> - The `docs/` directory is the single source of truth; legacy per-layer docs (`data/docs/`, `interfaces/docs/`, `observability/docs/`) are kept for reference but should not be updated.
> - Always run `mkdocs serve` before committing — broken links and malformed tables are the most common PR feedback.
> - Cross-reference liberally: a link from troubleshooting to GPU configuration is better than duplicating the NVIDIA toolkit installation steps.
