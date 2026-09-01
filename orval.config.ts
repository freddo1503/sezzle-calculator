import { defineConfig } from "orval";

// Generated from the contract, never hand-written. See
// docs/decisions/0008-generate-all-wire-types.md.
//
// Two outputs, because they do different jobs. `client` gives compile-time types
// and a typed fetch wrapper, which TypeScript erases at build time and which
// therefore checks nothing at runtime. `zod` gives schemas that validate the
// actual response at the boundary, so a backend that violated the contract fails
// loudly and locally instead of handing the interface a shape TypeScript believed
// was correct.

export default defineConfig({
  client: {
    input: "./openapi.yaml",
    output: {
      mode: "split",
      target: "./frontend/src/api/calculator.ts",
      schemas: "./frontend/src/api/model",
      client: "fetch",
      baseUrl: "/api",
      prettier: false,
      biome: true,
    },
  },
  zod: {
    input: "./openapi.yaml",
    output: {
      mode: "single",
      client: "zod",
      target: "./frontend/src/api/schemas.zod.ts",
      prettier: false,
      biome: true,
    },
  },
});
