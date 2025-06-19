import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { z } from "zod";
import { spawn } from "child_process";
import path from "path";

// Helper function to execute Python CAS scripts
async function executePythonScript(functionName: string, params: any = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
import os
import json
sys.path.append('${path.join(process.cwd(), 'backend')}')

try:
    from production_cas import ${functionName}
    
    if '${functionName}' == 'test_cas_server_connection':
        result = ${functionName}()
    elif '${functionName}' == 'load_topic_vectors_preview':
        result = ${functionName}(${params.rows || 5})
    else:
        result = ${functionName}('${params.case_number}', ${params.top_k || 5})
    
    print(json.dumps(result))
except Exception as e:
    error_result = {
        "status": "error",
        "error": str(e),
        "message": f"Python execution failed: {str(e)}"
    }
    print(json.dumps(error_result))
`;

    const python = spawn('python3', ['-c', pythonScript], {
      cwd: process.cwd(),
      env: { ...process.env }
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script failed: ${stderr || 'Unknown error'}`));
        return;
      }

      try {
        const result = JSON.parse(stdout.trim());
        if (result.status === 'error') {
          reject(new Error(result.message));
        } else {
          resolve(result);
        }
      } catch (parseError) {
        reject(new Error(`Failed to parse Python output: ${stdout}`));
      }
    });
  });
}

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

  // CAS server status endpoint
  app.get("/api/cas-status", async (req, res) => {
    try {
      const result = await executePythonScript('test_cas_server_connection');
      res.json(result);
    } catch (error) {
      res.status(503).json({
        status: "connection_failed",
        error: error.message,
        message: "CAS server connection failed - requires VPN access to trck1056928.trc.sas.com"
      });
    }
  });

  // Table preview endpoint
  app.get("/api/table-preview", async (req, res) => {
    try {
      const result = await executePythonScript('load_topic_vectors_preview', { rows: 5 });
      res.json({
        success: true,
        data: result,
        message: `Successfully loaded ${result.length} rows from topic_vectors table`
      });
    } catch (error) {
      res.status(503).json({
        success: false,
        error: "CAS connection failed",
        message: error.message,
        note: "Server requires VPN access. Test locally with network access to trck1056928.trc.sas.com"
      });
    }
  });

  // Similarity search endpoint
  app.post("/api/search-similar", async (req, res) => {
    try {
      const { case_number, top_k = 5 } = req.body;
      
      if (!case_number) {
        return res.status(400).json({
          success: false,
          error: "case_number is required"
        });
      }

      const result = await executePythonScript('get_similar_cases', { 
        case_number, 
        top_k: Math.min(top_k, 20) 
      });
      
      res.json({
        success: true,
        case_number,
        similar_cases: result,
        total_found: result.length
      });
    } catch (error) {
      res.status(503).json({
        success: false,
        error: "Similarity search failed",
        message: error.message,
        note: "Requires connection to SAS Viya server"
      });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
