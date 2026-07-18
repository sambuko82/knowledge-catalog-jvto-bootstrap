# JVTO Destinations MCP Server

Read-only MCP server exposing JVTO's public destination data (Kawah Ijen,
Mount Bromo, Tumpak Sewu, Madakaripura, Papuma Beach) from the published OKF
bundle at `../okf/bundles/jvto/`.

## Setup

    npm install
    npm run build

## Run standalone (for local testing)

    npm start

The server speaks MCP over stdio — it expects an MCP client on the other end,
not a human at a terminal.

## Verify it works

    npm test          # unit tests for the bundle data-access layer
    npm run smoke-test  # end-to-end: builds nothing itself, so run `npm run build` first

## Tools

- `list_destinations` — list all destinations (id, title, description, tags, status, last_verified).
- `search_destinations` — `{ query: string }`, case-insensitive substring match on title/description/tags.
- `get_destination` — `{ id: string }` (accepts `"kawah-ijen"` or `"destinations/kawah-ijen"`), returns full frontmatter + markdown body.

## Resources

Each destination is also exposed as a resource at `destination://<slug>`
(e.g. `destination://kawah-ijen`), returning the raw markdown body.

## Adding to an MCP client

Most MCP clients (Claude Desktop, etc.) take a JSON config block like:

    {
      "mcpServers": {
        "jvto-destinations": {
          "command": "node",
          "args": ["/absolute/path/to/mcp-server/dist/index.js"]
        }
      }
    }

Claude Code can also register it via its `claude mcp add` command — run
`claude mcp add --help` for the current syntax, since it varies by version.

## Data source

Reads only from the public bundle (`okf/bundles/jvto/catalog.json` and
`okf/bundles/jvto/destinations/*.md`) — never from the curation YAML in
`okf/jvto/curation/`. It never writes to any file. Regenerate the bundle with
`python okf/jvto/scripts/build_bundle.py --curated --indexes` (see the root
`CLAUDE.md`) if destination data changes; this server picks up the new files
on its next read, with no restart-time caching to invalidate.
