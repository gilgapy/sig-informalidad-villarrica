import { z } from 'zod';

export interface ProjectMetadata {
  readonly title: string;
  readonly socialProblem: string;
  readonly institution: string;
  readonly faculty: string;
  readonly career: string;
  readonly semester: string;
  readonly course: string;
  readonly location: string;
  readonly academicYear: number;
  readonly subjects: readonly string[];
  readonly facultyStaff: readonly string[];
  readonly studentGroup: string;
}

export interface ProjectObjective {
  readonly id: string;
  readonly description: string;
}

export interface MethodologicalStep {
  readonly stepNumber: number;
  readonly title: string;
  readonly objectives: readonly string[];
}

export interface SessionPlan {
  readonly sessionNumber: number;
  readonly date: string;
  readonly day: string;
  readonly focus: string;
  readonly details: string;
}

export interface RubricIndicator {
  readonly id: number;
  readonly title: string;
  readonly points: number;
  readonly criteria: string;
  readonly justification: readonly string[];
}

export interface ApiResponse<T> {
  readonly success: boolean;
  readonly data?: T;
  readonly error?: string;
  readonly meta?: Record<string, unknown>;
}

export const QuerySessionSchema = z.object({
  sessionNumber: z.number().int().min(1).max(17).optional(),
  date: z.string().optional()
});

export const QueryRubricSchema = z.object({
  indicatorNumber: z.number().int().min(1).max(6)
});

export const SearchTopicsSchema = z.object({
  query: z.string().min(2)
});

export type QuerySessionInput = z.infer<typeof QuerySessionSchema>;
export type QueryRubricInput = z.infer<typeof QueryRubricSchema>;
export type SearchTopicsInput = z.infer<typeof SearchTopicsSchema>;
