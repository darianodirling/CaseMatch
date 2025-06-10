import { users, cases, type User, type InsertUser, type Case, type InsertCase } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getAllCases(): Promise<Case[]>;
  searchCases(query: string): Promise<Case[]>;
  filterCases(filters: {
    assignmentGroup?: string;
    caseType?: string;
    status?: string;
  }): Promise<Case[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private cases: Map<number, Case>;
  private currentUserId: number;
  private currentCaseId: number;

  constructor() {
    this.users = new Map();
    this.cases = new Map();
    this.currentUserId = 1;
    this.currentCaseId = 1;
    
    // Initialize with sample case data
    this.initializeCases();
  }

  private initializeCases() {
    const sampleCases: InsertCase[] = [
      {
        number: "CS10023856",
        title: "Database connection issues observed in SAS.",
        resolution: "Configured ODBC settings as per KB0034127, restoring connection functionality.",
        similarity: 93,
        externalUrl: "https://communities.sas.com/t5/SAS-Communities-Library/Case-CS10023856/ta-p/123456",
        assignmentGroup: "database",
        caseType: "bug",
        status: "resolved"
      },
      {
        number: "CS13458729",
        title: "User reported intermittent performance lags in SAS Studio.",
        resolution: "Confirmed system resources and adjusted configuration ran settings as recommended.",
        similarity: 87,
        externalUrl: "https://communities.sas.com/t5/SAS-Communities-Library/Case-CS13458729/ta-p/234567",
        assignmentGroup: "performance",
        caseType: "performance",
        status: "resolved"
      },
      {
        number: "CS18904562",
        title: "SAML authentication troubles with SAS platform.",
        resolution: "Reconfigured SAML settings in accordance with KB0039 956, resolved authentication problems.",
        similarity: 82,
        externalUrl: "https://communities.sas.com/t5/SAS-Communities-Library/Case-CS18904562/ta-p/345678",
        assignmentGroup: "security",
        caseType: "configuration",
        status: "resolved"
      },
      {
        number: "CS20456789",
        title: "SAS Visual Analytics dashboard loading errors.",
        resolution: "Updated browser compatibility settings and cleared cache to resolve display issues.",
        similarity: 91,
        externalUrl: "https://communities.sas.com/t5/SAS-Communities-Library/Case-CS20456789/ta-p/456789",
        assignmentGroup: "performance",
        caseType: "bug",
        status: "in-progress"
      },
      {
        number: "CS22789012",
        title: "Enterprise Guide connection timeout issues.",
        resolution: "Adjusted server timeout settings and network configuration parameters.",
        similarity: 88,
        externalUrl: "https://communities.sas.com/t5/SAS-Communities-Library/Case-CS22789012/ta-p/567890",
        assignmentGroup: "database",
        caseType: "configuration",
        status: "open"
      }
    ];

    sampleCases.forEach(caseData => {
      const id = this.currentCaseId++;
      const caseItem: Case = { ...caseData, id };
      this.cases.set(id, caseItem);
    });
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async getAllCases(): Promise<Case[]> {
    return Array.from(this.cases.values()).sort((a, b) => b.similarity - a.similarity);
  }

  async searchCases(query: string): Promise<Case[]> {
    const lowercaseQuery = query.toLowerCase();
    return Array.from(this.cases.values())
      .filter(caseItem => 
        caseItem.title.toLowerCase().includes(lowercaseQuery) ||
        caseItem.resolution.toLowerCase().includes(lowercaseQuery) ||
        caseItem.number.toLowerCase().includes(lowercaseQuery)
      )
      .sort((a, b) => b.similarity - a.similarity);
  }

  async filterCases(filters: {
    assignmentGroup?: string;
    caseType?: string;
    status?: string;
  }): Promise<Case[]> {
    return Array.from(this.cases.values())
      .filter(caseItem => {
        if (filters.assignmentGroup && caseItem.assignmentGroup !== filters.assignmentGroup) {
          return false;
        }
        if (filters.caseType && caseItem.caseType !== filters.caseType) {
          return false;
        }
        if (filters.status && caseItem.status !== filters.status) {
          return false;
        }
        return true;
      })
      .sort((a, b) => b.similarity - a.similarity);
  }
}

export const storage = new MemStorage();
