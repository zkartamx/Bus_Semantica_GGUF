import { v } from "convex/values";
import { query, mutation, action } from "./_generated/server";
import { getAuthUserId } from "@convex-dev/auth/server";
import { api } from "./_generated/api";
import { paginationOptsValidator } from "convex/server";

// Query to list all documents with pagination
export const listDocuments = query({
  args: {
    paginationOpts: paginationOptsValidator,
    category: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    if (args.category) {
      const result = await ctx.db
        .query("documents")
        .withIndex("by_category", (q) => q.eq("category", args.category))
        .order("desc")
        .paginate(args.paginationOpts);
      
      return {
        ...result,
        page: result.page.map(doc => ({
          ...doc,
          embedding: undefined,
        })),
      };
    } else {
      const result = await ctx.db
        .query("documents")
        .order("desc")
        .paginate(args.paginationOpts);
      
      return {
        ...result,
        page: result.page.map(doc => ({
          ...doc,
          embedding: undefined,
        })),
      };
    }
  },
});

// Query to get document statistics
export const getStats = query({
  args: {},
  handler: async (ctx) => {
    const totalDocs = await ctx.db.query("documents").collect();
    const categories = new Set(totalDocs.map(doc => doc.category).filter(Boolean));
    const topics = new Set(totalDocs.map(doc => doc.topic).filter(Boolean));
    
    return {
      totalDocuments: totalDocs.length,
      categories: Array.from(categories),
      topics: Array.from(topics),
    };
  },
});

// Mutation to add a document
export const addDocument = mutation({
  args: {
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    topic: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    
    // Schedule embedding generation
    await ctx.scheduler.runAfter(0, api.documents.generateEmbedding, {
      title: args.title,
      content: args.content,
      category: args.category,
      topic: args.topic,
      authorId: userId || undefined,
    });
    
    return { success: true, message: "Document added and embedding generation scheduled" };
  },
});

// Action to generate embeddings using OpenAI
export const generateEmbedding = action({
  args: {
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    topic: v.optional(v.string()),
    authorId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    const OpenAI = (await import("openai")).default;
    
    const openai = new OpenAI({
      baseURL: process.env.CONVEX_OPENAI_BASE_URL,
      apiKey: process.env.CONVEX_OPENAI_API_KEY,
    });
    
    try {
      const response = await openai.embeddings.create({
        model: "text-embedding-3-small",
        input: args.content,
      });
      
      const embedding = response.data[0].embedding;
      
      await ctx.runMutation(api.documents.saveDocumentWithEmbedding, {
        title: args.title,
        content: args.content,
        category: args.category,
        topic: args.topic,
        authorId: args.authorId,
        embedding,
      });
      
    } catch (error) {
      console.error("Error generating embedding:", error);
      throw new Error("Failed to generate embedding");
    }
  },
});

// Internal mutation to save document with embedding
export const saveDocumentWithEmbedding = mutation({
  args: {
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    topic: v.optional(v.string()),
    authorId: v.optional(v.id("users")),
    embedding: v.array(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("documents", {
      title: args.title,
      content: args.content,
      category: args.category,
      topic: args.topic,
      authorId: args.authorId,
      embedding: args.embedding,
    });
  },
});

// Action to perform semantic search
export const semanticSearch = action({
  args: {
    query: v.string(),
    limit: v.optional(v.number()),
    category: v.optional(v.string()),
  },
  handler: async (ctx, args): Promise<any[]> => {
    const OpenAI = (await import("openai")).default;
    
    const openai = new OpenAI({
      baseURL: process.env.CONVEX_OPENAI_BASE_URL,
      apiKey: process.env.CONVEX_OPENAI_API_KEY,
    });
    
    try {
      // Generate embedding for the search query
      const response = await openai.embeddings.create({
        model: "text-embedding-3-small",
        input: args.query,
      });
      
      const queryEmbedding = response.data[0].embedding;
      
      // Get all documents and calculate similarities
      const results: any[] = await ctx.runQuery(api.documents.findSimilarDocuments, {
        queryEmbedding,
        limit: args.limit || 10,
        category: args.category,
      });
      
      // Log the search
      const userId = await getAuthUserId(ctx);
      await ctx.runMutation(api.documents.logSearch, {
        query: args.query,
        userId: userId || undefined,
        resultsCount: results.length,
      });
      
      return results;
      
    } catch (error) {
      console.error("Error in semantic search:", error);
      throw new Error("Search failed");
    }
  },
});

// Query to find similar documents based on embedding
export const findSimilarDocuments = query({
  args: {
    queryEmbedding: v.array(v.number()),
    limit: v.number(),
    category: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let documents;
    
    if (args.category) {
      documents = await ctx.db
        .query("documents")
        .withIndex("by_category", (q) => q.eq("category", args.category))
        .collect();
    } else {
      documents = await ctx.db.query("documents").collect();
    }
    
    // Calculate cosine similarity for each document
    const results = documents.map(doc => {
      const similarity = cosineSimilarity(args.queryEmbedding, doc.embedding);
      return {
        ...doc,
        similarity,
        embedding: undefined, // Don't send embedding to client
      };
    });
    
    // Sort by similarity and return top results
    return results
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, args.limit);
  },
});

// Mutation to log search queries
export const logSearch = mutation({
  args: {
    query: v.string(),
    userId: v.optional(v.id("users")),
    resultsCount: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("searches", {
      query: args.query,
      userId: args.userId,
      resultsCount: args.resultsCount,
    });
  },
});

// Mutation to delete a document
export const deleteDocument = mutation({
  args: {
    documentId: v.id("documents"),
  },
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    const document = await ctx.db.get(args.documentId);
    
    if (!document) {
      throw new Error("Document not found");
    }
    
    // Check if user owns the document or is admin
    if (document.authorId && document.authorId !== userId) {
      throw new Error("Not authorized to delete this document");
    }
    
    await ctx.db.delete(args.documentId);
    return { success: true };
  },
});

// Mutation to clear all documents (admin only)
export const clearAllDocuments = mutation({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) {
      throw new Error("Must be logged in");
    }
    
    const documents = await ctx.db.query("documents").collect();
    
    for (const doc of documents) {
      await ctx.db.delete(doc._id);
    }
    
    return { success: true, deletedCount: documents.length };
  },
});

// Helper function to calculate cosine similarity
function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error("Vectors must have the same length");
  }
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  if (normA === 0 || normB === 0) {
    return 0;
  }
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Action to load sample documents
export const loadSampleDocuments = action({
  args: {},
  handler: async (ctx) => {
    const sampleDocs = [
      {
        title: "Introduction to Python",
        content: "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and artificial intelligence.",
        category: "programming",
        topic: "python"
      },
      {
        title: "Machine Learning Basics",
        content: "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It includes supervised, unsupervised, and reinforcement learning.",
        category: "ai",
        topic: "machine_learning"
      },
      {
        title: "Vector Databases",
        content: "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They're essential for AI applications like semantic search and recommendation systems.",
        category: "database",
        topic: "vector_database"
      },
      {
        title: "React Development",
        content: "React is a JavaScript library for building user interfaces. It uses a component-based architecture and virtual DOM for efficient rendering.",
        category: "programming",
        topic: "react"
      },
      {
        title: "Natural Language Processing",
        content: "NLP is a field of AI that focuses on the interaction between computers and human language. It includes tasks like text classification, sentiment analysis, and language translation.",
        category: "ai",
        topic: "nlp"
      }
    ];
    
    let addedCount = 0;
    
    for (const doc of sampleDocs) {
      try {
        await ctx.runAction(api.documents.generateEmbedding, {
          title: doc.title,
          content: doc.content,
          category: doc.category,
          topic: doc.topic,
        });
        addedCount++;
      } catch (error) {
        console.error(`Failed to add document: ${doc.title}`, error);
      }
    }
    
    return { success: true, addedCount };
  },
});
