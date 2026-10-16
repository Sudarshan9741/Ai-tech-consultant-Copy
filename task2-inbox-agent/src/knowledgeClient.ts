import { GroundingSource } from "./types.js";

export interface KnowledgeBrainResponse {
  answered: boolean;
  answer: string;
  confidence: number;
  escalation_id: number | null;
  sources: GroundingSource[];
  images: Array<{
    url: string;
    alt: string;
    caption: string;
    article_title: string;
    article_url: string;
  }>;
}

export class KnowledgeBrainClient {
  private baseUrl: string;

  constructor(baseUrl = process.env.TASK1_API_URL || "http://127.0.0.1:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async checkHealth(): Promise<{ status: string; active_articles: number }> {
    try {
      const resp = await fetch(`${this.baseUrl}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      });
      if (!resp.ok) {
        throw new Error(`Health check returned ${resp.status}`);
      }
      return (await resp.json()) as { status: string; active_articles: number };
    } catch (err) {
      throw new Error(`Failed to connect to Task 1 Knowledge Brain at ${this.baseUrl}: ${err}`);
    }
  }

  async ask(question: string): Promise<KnowledgeBrainResponse> {
    try {
      const resp = await fetch(`${this.baseUrl}/api/v1/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      if (!resp.ok) {
        throw new Error(`Knowledge Brain API returned HTTP ${resp.status}`);
      }

      const data = (await resp.json()) as KnowledgeBrainResponse;
      return data;
    } catch (err) {
      // Return safe fallback if Knowledge Brain is temporarily unreachable
      return {
        answered: false,
        answer: "Knowledge Brain API is currently unreachable. Escalating to human support.",
        confidence: 0.0,
        escalation_id: null,
        sources: [],
        images: []
      };
    }
  }
}

export const knowledgeClient = new KnowledgeBrainClient();
