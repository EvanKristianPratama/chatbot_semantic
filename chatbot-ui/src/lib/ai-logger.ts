// AI Logging System for GadgetBot
// Tracks all AI interactions for analytics and debugging

import { AILogEntry, QueryIntent } from '@/types';
import { generateId } from './utils';
import { detectIntent, extractParams } from './ai-context';

class AILogger {
    private logs: AILogEntry[] = [];
    private maxLogs: number = 1000;

    log(entry: Omit<AILogEntry, 'id' | 'timestamp'>): AILogEntry {
        const fullEntry: AILogEntry = {
            id: generateId(),
            timestamp: new Date(),
            ...entry,
        };

        this.logs.push(fullEntry);

        // Keep only last maxLogs entries
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }

        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.log('[AILog]', {
                intent: fullEntry.detectedIntent,
                params: fullEntry.extractedParams,
                latency: fullEntry.latencyMs,
            });
        }

        return fullEntry;
    }

    createEntry(
        sessionId: string,
        userMessage: string,
        aiResponse: string,
        startTime: number,
        productsRecommended: string[] = [],
        wasFiltered: boolean = false,
        filterReason?: string
    ): AILogEntry {
        const endTime = Date.now();
        const intent = detectIntent(userMessage);
        const params = extractParams(userMessage);

        return this.log({
            sessionId,
            userMessage,
            detectedIntent: intent,
            extractedParams: params,
            promptUsed: 'default',
            modelUsed: 'simulated',
            tokensUsed: {
                input: userMessage.length,
                output: aiResponse.length,
            },
            latencyMs: endTime - startTime,
            aiResponse,
            productsRecommended,
            wasFiltered,
            filterReason,
            userFeedback: null,
            followUpAsked: false,
        });
    }

    getStats(): {
        totalQueries: number;
        avgLatencyMs: number;
        intentDistribution: Record<string, number>;
        topBrands: Record<string, number>;
        filterRate: number;
    } {
        const totalQueries = this.logs.length;

        if (totalQueries === 0) {
            return {
                totalQueries: 0,
                avgLatencyMs: 0,
                intentDistribution: {},
                topBrands: {},
                filterRate: 0,
            };
        }

        const avgLatencyMs = this.logs.reduce((sum, log) => sum + log.latencyMs, 0) / totalQueries;

        const intentDistribution: Record<string, number> = {};
        const topBrands: Record<string, number> = {};
        let filteredCount = 0;

        for (const log of this.logs) {
            // Count intents
            intentDistribution[log.detectedIntent] = (intentDistribution[log.detectedIntent] || 0) + 1;

            // Count brands
            if (log.extractedParams.brand) {
                topBrands[log.extractedParams.brand] = (topBrands[log.extractedParams.brand] || 0) + 1;
            }

            // Count filtered
            if (log.wasFiltered) filteredCount++;
        }

        return {
            totalQueries,
            avgLatencyMs: Math.round(avgLatencyMs),
            intentDistribution,
            topBrands,
            filterRate: (filteredCount / totalQueries) * 100,
        };
    }

    getLogs(limit: number = 100): AILogEntry[] {
        return this.logs.slice(-limit);
    }

    getLogsBySession(sessionId: string): AILogEntry[] {
        return this.logs.filter(log => log.sessionId === sessionId);
    }

    addFeedback(logId: string, feedback: 'positive' | 'negative'): boolean {
        const log = this.logs.find(l => l.id === logId);
        if (log) {
            log.userFeedback = feedback;
            return true;
        }
        return false;
    }

    exportLogs(): string {
        return JSON.stringify(this.logs, null, 2);
    }

    clearLogs(): void {
        this.logs = [];
    }
}

// Singleton instance
export const aiLogger = new AILogger();

// Helper function for quick logging
export function logAIInteraction(
    sessionId: string,
    userMessage: string,
    aiResponse: string,
    startTime: number,
    options?: {
        productsRecommended?: string[];
        wasFiltered?: boolean;
        filterReason?: string;
    }
): AILogEntry {
    return aiLogger.createEntry(
        sessionId,
        userMessage,
        aiResponse,
        startTime,
        options?.productsRecommended,
        options?.wasFiltered,
        options?.filterReason
    );
}
