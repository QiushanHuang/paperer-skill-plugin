# Sync Policy

This skill is authored in `paperer-skill-plugin` and mirrored into `Paperer`.

## Source of truth

`paperer-skill-plugin` is the public source repository for the skill module.

Sync direction:

`paperer-skill-plugin -> Paperer`

## What to mirror

Mirror the skill package and supporting files, including:

- `SKILL.md`
- `agents/openai.yaml`
- `references/*`
- any future assets or module files that belong to this skill

## What not to treat as source

Do not treat `Paperer` as an independent source of truth for mirrored skill files.

Generated paper bundles are runtime artifacts and should be managed separately from the skill source tree unless a later workflow explicitly requires them in `Paperer`.
