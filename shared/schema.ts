import { pgTable, text, serial, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const cases = pgTable("cases", {
  id: serial("id").primaryKey(),
  number: text("number").notNull().unique(),
  title: text("title").notNull(),
  resolution: text("resolution").notNull(),
  similarity: integer("similarity").notNull(),
  externalUrl: text("external_url").notNull(),
  assignmentGroup: text("assignment_group").notNull(),
  caseType: text("case_type").notNull(),
  status: text("status").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertCaseSchema = createInsertSchema(cases).omit({
  id: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type InsertCase = z.infer<typeof insertCaseSchema>;
export type Case = typeof cases.$inferSelect;
