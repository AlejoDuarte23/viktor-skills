# VIKTOR Skills

Agent skills for building VIKTOR apps.

Each skill lives in `skills/<skill-name>/` and contains:

- `SKILL.md`
- `reference.md`
- `examples.md`

## Quick Install

Install the skills into Claude Code and Codex with the open `skills` CLI:

```bash
npx skills add AlejoDuarte23/viktor-skills --skill '*' -a claude-code -a codex -g
```

Use `-g` for a global user install. Omit `-g` to install into the current project. Install all skills, not only `viktor`; the router skill links to the specialized VIKTOR skills.

## Codex

For Codex, use the `npx skills` command above. After installing, start a new Codex thread and mention the router skill:

```text
$viktor
```

Codex can also pick the skill automatically when you ask for VIKTOR app work.

## Claude Code

In Claude Code, invoke the router with:

```text
/viktor
```

## Claude Code Marketplace

Claude Code can also install this repository as a plugin marketplace:

```text
/plugin marketplace add AlejoDuarte23/viktor-skills
/plugin install viktor-skills@viktor-skills
/reload-plugins
```

Marketplace plugin skills are namespaced, so invoke the router with:

```text
/viktor-skills:viktor
```

See [INSTALL.md](INSTALL.md) for Windows PowerShell, manual copy, update, and troubleshooting notes.
