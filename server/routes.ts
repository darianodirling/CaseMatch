import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  // Get all cases
  app.get("/api/cases", async (req, res) => {
    try {
      const cases = await storage.getAllCases();
      res.json(cases);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch cases" });
    }
  });

  // Search cases
  app.get("/api/cases/search", async (req, res) => {
    try {
      const { q } = req.query;
      
      if (!q || typeof q !== 'string') {
        const cases = await storage.getAllCases();
        return res.json(cases);
      }

      const cases = await storage.searchCases(q);
      res.json(cases);
    } catch (error) {
      res.status(500).json({ message: "Failed to search cases" });
    }
  });

  // Filter cases
  app.get("/api/cases/filter", async (req, res) => {
    try {
      const { assignmentGroup, caseType, status } = req.query;
      
      const filters: {
        assignmentGroup?: string;
        caseType?: string;
        status?: string;
      } = {};

      if (assignmentGroup && typeof assignmentGroup === 'string') {
        filters.assignmentGroup = assignmentGroup;
      }
      if (caseType && typeof caseType === 'string') {
        filters.caseType = caseType;
      }
      if (status && typeof status === 'string') {
        filters.status = status;
      }

      const cases = await storage.filterCases(filters);
      res.json(cases);
    } catch (error) {
      res.status(500).json({ message: "Failed to filter cases" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
