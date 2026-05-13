# VIKTOR Skills

Agent skills for building VIKTOR apps.

Each skill lives in `skills/<skill-name>/` and contains:

- `SKILL.md`
- `reference.md`
- `examples.md`

## Install For Codex

From this repository:

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

Or symlink them so local repo edits are picked up:

```bash
mkdir -p ~/.codex/skills
for skill in skills/*; do
  ln -sfn "$(pwd)/$skill" "$HOME/.codex/skills/$(basename "$skill")"
done
```

Restart Codex if the skills do not appear in the current session.

## Install For Claude Code

Install globally for your user:

```bash
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

Or symlink them:

```bash
mkdir -p ~/.claude/skills
for skill in skills/*; do
  ln -sfn "$(pwd)/$skill" "$HOME/.claude/skills/$(basename "$skill")"
done
```

Install only for one project:

```bash
mkdir -p /path/to/project/.claude/skills
cp -R skills/* /path/to/project/.claude/skills/
```

Claude Code can invoke a skill directly with:

```text
/viktor
```

Restart Claude Code if the `.claude/skills` directory did not exist when the session started.

## Update Installed Skills

If copied:

```bash
cp -R skills/* ~/.codex/skills/
cp -R skills/* ~/.claude/skills/
```

If symlinked, pull or edit this repository; no copy step is needed.
