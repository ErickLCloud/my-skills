# my-skills

Personal Claude skills packaged as a Claude Code plugin marketplace. Each skill is its own plugin.

| Plugin | What it does |
|---|---|
| `sharpen` | Turns a vague or multi-stage request into a work brief, confirmed before work starts |
| `multi-work` | Plans multi-session work: interview → plan doc → pilot/worker prompts → retro |
| `revision-retro` | Reviews why a deliverable went through many `_vN` revisions and proposes rules |
| `pptx-report-style` | Layout and wording rules for engineering PowerPoint reports, plus a lint script |
| `project-init` | Scaffolds the standard project-workspace layout |

## Install (Claude Code)

```
/plugin marketplace add ErickLCloud/my-skills
/plugin install sharpen@my-skills
```

Update later with `/plugin marketplace update my-skills`.

## claude.ai

The web app installs skills from `.skill` files (Settings > Capabilities), not from this marketplace.
Zip a folder under `skills/` with `SKILL.md` at the archive root and rename it to `.skill`.

## Layout

```
.claude-plugin/marketplace.json   one plugin entry per skill
skills/<name>/SKILL.md            frontmatter (name, description) + instructions
skills/<name>/reference|scripts|assets/   loaded on demand
```

This repo is generated from the author's working sources; edit there, not here.
