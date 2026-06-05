# .claude/

Project-local Claude Code configuration for NetBox.

The tool-agnostic content layer for this repo is [`AGENTS.md`](../AGENTS.md) at the repo root, with its `CLAUDE.md` shim. This `.claude/` directory is the Claude-specific action layer that complements `AGENTS.md` with project-local skills, slash commands, and per-developer settings.

## Layout

- `skills/` — Project-local Claude Code skills. Each skill is its own subdirectory containing a `SKILL.md` describing what it does and when to use it. Use this for repo-specific procedures.
- `commands/` — Project-local slash commands. One Markdown file per command: `commands/<command-name>.md`. Use this for `/foo` shortcuts that only make sense in this repo.
- `settings.local.json` — Per-developer Claude Code settings (tool permissions, MCP server paths, IDE preferences). **Never committed** — this filename is in the repo's `.gitignore`.

## When to add a skill (vs. inlining in AGENTS.md or promoting upstream)

Add a skill here when:

- The procedure is repo-specific (it would not be useful in other NBL repos as-is).
- The procedure is non-trivial (more than a one-line note that fits naturally inside `AGENTS.md`).
- The procedure is a recipe an agent or engineer might re-run, not a one-off.

## When to add a slash command

Add a command here when:

- The action is something you find yourself typing the same prompt for repeatedly.
- The repo has a non-obvious workflow that benefits from a shortcut.

## Conventions

- Skill and command names use `lowercase-kebab-case`, matching the [folder naming convention in `AGENTS.md`](../AGENTS.md).
- Each skill directory has a `SKILL.md` (the entry point); supporting files (references, examples, sample data) live alongside it inside the skill's directory.
- Each command is a single Markdown file named for the slash command: `commands/<command-name>.md`.
- Skills and commands document *why* they make the choices they do — the rationale is more durable than the bare instruction.

## How to add your first skill

1. Pick a kebab-case name describing the action: e.g., `parse-linear-issues`, `render-delivery-row`.
2. `mkdir .claude/skills/<skill-name>/` and create `SKILL.md` inside it.
3. The `SKILL.md` opens with a short YAML-ish header (name, description, version) and then the prompt content.
4. Open a PR — the new directory and its `SKILL.md` are tracked once committed.

## References

- [`AGENTS.md`](../AGENTS.md) — this repo's primary agent-context file (open standard).
- [Claude Code skills documentation](https://docs.claude.com/en/docs/claude-code/skills) — what a `SKILL.md` looks like and how Claude Code resolves them.
