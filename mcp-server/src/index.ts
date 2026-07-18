#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createDestinationsMcpServer } from "./server.js";

const server = createDestinationsMcpServer();
const transport = new StdioServerTransport();
await server.connect(transport);
