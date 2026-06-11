# validate_editorconfig.py

Validates one or more files against an `.editorconfig` using `ec-windows-amd64.exe`.

## Synopsis

```
~/.claude/skills/code-review-react-nextjs/tools/validate_editorconfig.py -c <editorconfig-dir> <file> [<file> ...]
```

## Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--editorconfig` | `-c` | Yes | Directory containing `.editorconfig`, relative to cwd |
| `files` | — | Yes | One or more file paths to validate, relative to cwd |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All files conform to the EditorConfig rules |
| non-zero | One or more violations found |

## Examples

Validate a single file:
```
~/.claude/skills/code-review-react-nextjs/tools/validate_editorconfig.py -c . src/app/page.tsx
```

Validate multiple files:
```
~/.claude/skills/code-review-react-nextjs/tools/validate_editorconfig.py -c . src/app/page.tsx src/components/Button.tsx
```

Validate using a non-root editorconfig:
```
~/.claude/skills/code-review-react-nextjs/tools/validate_editorconfig.py -c packages/ui packages/ui/src/index.ts
```

## Notes

- All paths are resolved relative to the current working directory at invocation time.
- `-c` must point to the **directory** containing `.editorconfig`, not the file itself.
- Output is printed directly to stdout/stderr as produced by `ec-windows-amd64.exe`.
- The script is a thin wrapper — all validation logic and output formatting is handled by the bundled `internal/ec-windows-amd64.exe` binary.
