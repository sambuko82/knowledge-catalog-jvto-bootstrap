import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  listDestinations,
  searchDestinations,
  getDestination,
  listDestinationResourceUris,
} from "./bundle.js";

export function createDestinationsMcpServer(): McpServer {
  const server = new McpServer({
    name: "jvto-destinations-mcp",
    version: "0.1.0",
  });

  server.registerTool(
    "list_destinations",
    {
      title: "List destinations",
      description:
        "List every JVTO destination in the public bundle (id, title, description, tags, status, last_verified).",
    },
    async () => ({
      content: [{ type: "text", text: JSON.stringify(listDestinations(), null, 2) }],
    })
  );

  server.registerTool(
    "search_destinations",
    {
      title: "Search destinations",
      description:
        "Case-insensitive substring search over destination title, description, and tags.",
      inputSchema: { query: z.string().min(1) },
    },
    async ({ query }) => ({
      content: [{ type: "text", text: JSON.stringify(searchDestinations(query), null, 2) }],
    })
  );

  server.registerTool(
    "get_destination",
    {
      title: "Get destination detail",
      description:
        "Full detail for one destination, by slug ('kawah-ijen') or full catalog id ('destinations/kawah-ijen').",
      inputSchema: { id: z.string().min(1) },
    },
    async ({ id }) => {
      const detail = getDestination(id);
      if (!detail) {
        return {
          isError: true,
          content: [{ type: "text", text: `destination not found: ${id}` }],
        };
      }
      return {
        content: [
          {
            type: "text",
            text: `${JSON.stringify(detail.frontmatter, null, 2)}\n\n${detail.body}`,
          },
        ],
      };
    }
  );

  server.registerResource(
    "destination",
    new ResourceTemplate("destination://{slug}", {
      list: async () => ({
        resources: listDestinationResourceUris().map(({ uri, title }) => ({
          uri,
          name: title,
          mimeType: "text/markdown",
        })),
      }),
    }),
    {
      title: "JVTO destination",
      description: "Raw markdown for one JVTO destination from the public bundle.",
      mimeType: "text/markdown",
    },
    async (uri, { slug }) => {
      const detail = getDestination(String(slug));
      if (!detail) {
        throw new Error(`destination not found: ${slug}`);
      }
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: detail.body }],
      };
    }
  );

  return server;
}
