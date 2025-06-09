import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
import { authTables } from "@convex-dev/auth/server";

const applicationTables = {
  documents: defineTable({
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    topic: v.optional(v.string()),
    embedding: v.array(v.number()),
    authorId: v.optional(v.id("users")),
  })
    .index("by_category", ["category"])
    .index("by_topic", ["topic"])
    .index("by_author", ["authorId"])
    .searchIndex("search_content", {
      searchField: "content",
      filterFields: ["category", "topic"],
    }),
  
  searches: defineTable({
    query: v.string(),
    userId: v.optional(v.id("users")),
    resultsCount: v.number(),
  })
    .index("by_user", ["userId"]),
};

export default defineSchema({
  ...authTables,
  ...applicationTables,
});
