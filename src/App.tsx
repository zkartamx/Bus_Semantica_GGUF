import { useState } from "react";
import { useQuery, useMutation, useAction } from "convex/react";
import { api } from "../convex/_generated/api";
import { useAuthActions } from "@convex-dev/auth/react";
import { Authenticated, Unauthenticated } from "convex/react";
import { SignInForm } from "./SignInForm";
import { SignOutButton } from "./SignOutButton";

import { Id } from "../convex/_generated/dataModel";

interface Document {
  _id: Id<"documents">;
  title: string;
  content: string;
  category?: string;
  topic?: string;
  similarity?: number;
  _creationTime: number;
}

interface SearchResult extends Document {
  similarity: number;
}

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<"search" | "manage" | "add">("search");
  
  // Document form state
  const [newDoc, setNewDoc] = useState({
    title: "",
    content: "",
    category: "",
    topic: ""
  });

  // Convex hooks
  const stats = useQuery(api.documents.getStats);
  const documents = useQuery(api.documents.listDocuments, {
    paginationOpts: { numItems: 20, cursor: null }
  });
  
  const addDocument = useMutation(api.documents.addDocument);
  const deleteDocument = useMutation(api.documents.deleteDocument);
  const clearAllDocuments = useMutation(api.documents.clearAllDocuments);
  const semanticSearch = useAction(api.documents.semanticSearch);
  const loadSampleDocuments = useAction(api.documents.loadSampleDocuments);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const results = await semanticSearch({
        query: searchQuery,
        limit: 10
      });
      setSearchResults(results as SearchResult[]);
    } catch (error) {
      console.error("Search failed:", error);
      alert("Search failed. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddDocument = async () => {
    if (!newDoc.title.trim() || !newDoc.content.trim()) {
      alert("Please fill in title and content");
      return;
    }

    try {
      await addDocument({
        title: newDoc.title,
        content: newDoc.content,
        category: newDoc.category || undefined,
        topic: newDoc.topic || undefined,
      });
      
      setNewDoc({ title: "", content: "", category: "", topic: "" });
      alert("Document added successfully!");
    } catch (error) {
      console.error("Failed to add document:", error);
      alert("Failed to add document. Please try again.");
    }
  };

  const handleLoadSample = async () => {
    try {
      const result = await loadSampleDocuments();
      alert(`Successfully loaded ${result.addedCount} sample documents!`);
    } catch (error) {
      console.error("Failed to load sample documents:", error);
      alert("Failed to load sample documents. Please try again.");
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to delete all documents? This cannot be undone.")) {
      return;
    }

    try {
      const result = await clearAllDocuments();
      alert(`Successfully deleted ${result.deletedCount} documents.`);
      setSearchResults([]);
    } catch (error) {
      console.error("Failed to clear documents:", error);
      alert("Failed to clear documents. Please try again.");
    }
  };

  const handleDeleteDocument = async (documentId: Id<"documents">) => {
    if (!confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await deleteDocument({ documentId });
      alert("Document deleted successfully!");
    } catch (error) {
      console.error("Failed to delete document:", error);
      alert("Failed to delete document. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Unauthenticated>
        <div className="flex items-center justify-center min-h-screen">
          <div className="max-w-md w-full">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🔍 Semantic Search
              </h1>
              <p className="text-gray-600">
                AI-powered document search with Convex
              </p>
            </div>
            <SignInForm />
          </div>
        </div>
      </Unauthenticated>

      <Authenticated>
        <div className="max-w-6xl mx-auto p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🔍 Semantic Search
              </h1>
              <p className="text-gray-600">
                AI-powered document search with vector embeddings
              </p>
            </div>
            <SignOutButton />
          </div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Total Documents</h3>
                <p className="text-2xl font-bold text-blue-600">{stats.totalDocuments}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Categories</h3>
                <p className="text-2xl font-bold text-green-600">{stats.categories.length}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Topics</h3>
                <p className="text-2xl font-bold text-purple-600">{stats.topics.length}</p>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                {[
                  { id: "search", label: "🔍 Search", icon: "🔍" },
                  { id: "manage", label: "📚 Manage", icon: "📚" },
                  { id: "add", label: "➕ Add Document", icon: "➕" }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Search Tab */}
          {activeTab === "search" && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4">Semantic Search</h2>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Enter your search query (e.g., 'machine learning algorithms')"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyDown={handleKeyPress}
                  />
                  <button
                    onClick={handleSearch}
                    disabled={isSearching || !searchQuery.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSearching ? "Searching..." : "Search"}
                  </button>
                </div>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-lg font-semibold mb-4">
                    Search Results ({searchResults.length})
                  </h3>
                  <div className="space-y-4">
                    {searchResults.map((result, index) => (
                      <div key={result._id} className="border-l-4 border-blue-500 pl-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-gray-900">{result.title}</h4>
                          <span className="text-sm text-blue-600 font-medium">
                            {(result.similarity * 100).toFixed(1)}% match
                          </span>
                        </div>
                        <p className="text-gray-700 mb-2">{result.content}</p>
                        <div className="flex gap-2 text-sm text-gray-500">
                          {result.category && (
                            <span className="bg-gray-100 px-2 py-1 rounded">
                              {result.category}
                            </span>
                          )}
                          {result.topic && (
                            <span className="bg-blue-100 px-2 py-1 rounded">
                              {result.topic}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Manage Tab */}
          {activeTab === "manage" && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4">Manage Documents</h2>
                <div className="flex gap-4 mb-6">
                  <button
                    onClick={handleLoadSample}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    📚 Load Sample Documents
                  </button>
                  <button
                    onClick={handleClearAll}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    🗑️ Clear All Documents
                  </button>
                </div>

                {documents && documents.page.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">All Documents</h3>
                    {documents.page.map((doc) => (
                      <div key={doc._id} className="border border-gray-200 p-4 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-gray-900">{doc.title}</h4>
                          <button
                            onClick={() => handleDeleteDocument(doc._id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Delete
                          </button>
                        </div>
                        <p className="text-gray-700 mb-2">{doc.content}</p>
                        <div className="flex gap-2 text-sm text-gray-500">
                          {doc.category && (
                            <span className="bg-gray-100 px-2 py-1 rounded">
                              {doc.category}
                            </span>
                          )}
                          {doc.topic && (
                            <span className="bg-blue-100 px-2 py-1 rounded">
                              {doc.topic}
                            </span>
                          )}
                          <span className="text-xs text-gray-400">
                            {new Date(doc._creationTime).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Add Document Tab */}
          {activeTab === "add" && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Add New Document</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={newDoc.title}
                    onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })}
                    placeholder="Enter document title"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content *
                  </label>
                  <textarea
                    value={newDoc.content}
                    onChange={(e) => setNewDoc({ ...newDoc, content: e.target.value })}
                    placeholder="Enter document content"
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <input
                      type="text"
                      value={newDoc.category}
                      onChange={(e) => setNewDoc({ ...newDoc, category: e.target.value })}
                      placeholder="e.g., programming, ai, database"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Topic
                    </label>
                    <input
                      type="text"
                      value={newDoc.topic}
                      onChange={(e) => setNewDoc({ ...newDoc, topic: e.target.value })}
                      placeholder="e.g., python, machine_learning"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                
                <button
                  onClick={handleAddDocument}
                  disabled={!newDoc.title.trim() || !newDoc.content.trim()}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ➕ Add Document
                </button>
              </div>
            </div>
          )}
        </div>
      </Authenticated>
    </div>
  );
}
