import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./server/routes";
import { setupVite, serveStatic, log } from "./server/vite";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // Setup development or production mode
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // Windows-compatible server binding
  const port = process.env.PORT || 3000;
  
  try {
    // Try binding to all interfaces first
    server.listen(port, '0.0.0.0', () => {
      log(`CaseMatch server running on http://localhost:${port}`);
      log(`Access your SAS dashboard at: http://localhost:${port}`);
    });
  } catch (error) {
    // Fallback to localhost only
    server.listen(port, 'localhost', () => {
      log(`CaseMatch server running on http://localhost:${port}`);
      log(`Access your SAS dashboard at: http://localhost:${port}`);
    });
  }
  
  server.on('error', (err: any) => {
    if (err.code === 'EADDRINUSE') {
      log(`Port ${port} is already in use. Try a different port or close other applications.`);
    } else if (err.code === 'ENOTSUP') {
      log(`Network configuration issue on Windows. Trying alternative port...`);
      // Try alternative port
      const altPort = parseInt(port.toString()) + 1;
      server.listen(altPort, 'localhost', () => {
        log(`CaseMatch server running on http://localhost:${altPort}`);
      });
    } else {
      log(`Server error: ${err.message}`);
    }
  });
})();