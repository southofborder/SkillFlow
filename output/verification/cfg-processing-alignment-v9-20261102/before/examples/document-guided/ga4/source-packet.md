File navigation (not proof of semantic coverage):
- skill/references/api-reference.md (403 physical lines)
- skill/scripts/package-lock.json (2513 physical lines)
- skill/scripts/package.json (17 physical lines)
- skill/scripts/setup.sh (2 physical lines)
- skill/scripts/src/api/bulk-lookup.ts (192 physical lines)
- skill/scripts/src/api/indexing.ts (193 physical lines)
- skill/scripts/src/api/metadata.ts (95 physical lines)
- skill/scripts/src/api/realtime.ts (99 physical lines)
- skill/scripts/src/api/reports.ts (175 physical lines)
- skill/scripts/src/api/searchConsole.ts (175 physical lines)
- skill/scripts/src/config/settings.ts (74 physical lines)
- skill/scripts/src/core/client.ts (133 physical lines)
- skill/scripts/src/core/storage.ts (171 physical lines)
- skill/scripts/src/index.ts (405 physical lines)
- skill/scripts/tsconfig.json (20 physical lines)
- skill/SKILL.md (158 physical lines)

SOURCE skill/references/api-reference.md:197-253
197: ## Search Console API
198: 
199: Import: `from './api/searchConsole.js'`
200: 
201: ### `querySearchAnalytics(options)`
202: 
203: Run a custom Search Console analytics query.
204: 
205: | Parameter | Type | Default | Description |
206: |-----------|------|---------|-------------|
207: | `options.dimensions` | `string[]` | `["query"]` | Dimensions: `query`, `page`, `device`, `country`, `searchAppearance` |
208: | `options.dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
209: | `options.rowLimit` | `number` | `1000` | Max rows |
210: | `options.startRow` | `number` | `0` | Pagination offset |
211: | `options.save` | `boolean` | `true` | Save results to JSON |
212: 
213: **Returns:** `Promise<SearchAnalyticsResponse>` — Rows with `{keys, clicks, impressions, ctr, position}`.
214: 
215: ### `getTopQueries(dateRange?)`
216: 
217: Get top 100 search queries by clicks.
218: 
219: | Parameter | Type | Default | Description |
220: |-----------|------|---------|-------------|
221: | `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
222: 
223: **Returns:** `Promise<SearchAnalyticsResponse>`
224: 
225: ### `getTopPages(dateRange?)`
226: 
227: Get top 100 pages by search impressions.
228: 
229: | Parameter | Type | Default | Description |
230: |-----------|------|---------|-------------|
231: | `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
232: 
233: **Returns:** `Promise<SearchAnalyticsResponse>`
234: 
235: ### `getDevicePerformance(dateRange?)`
236: 
237: Get search performance breakdown by device type (desktop, mobile, tablet).
238: 
239: | Parameter | Type | Default | Description |
240: |-----------|------|---------|-------------|
241: | `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
242: 
243: **Returns:** `Promise<SearchAnalyticsResponse>`
244: 
245: ### `getCountryPerformance(dateRange?)`
246: 
247: Get search performance by country (top 50).
248: 
249: | Parameter | Type | Default | Description |
250: |-----------|------|---------|-------------|
251: | `dateRange` | `string \| SearchConsoleDateRange` | `"30d"` | Date range |
252: 
253: **Returns:** `Promise<SearchAnalyticsResponse>`


SOURCE skill/references/api-reference.md:356-371
356: ## Storage
357: 
358: Import: `from './core/storage.js'`
359: 
360: ### `saveResult<T>(data, category, operation, extraInfo?)`
361: 
362: Save result data to a timestamped JSON file with metadata wrapper.
363: 
364: | Parameter | Type | Default | Description |
365: |-----------|------|---------|-------------|
366: | `data` | `T` | required | Data to save |
367: | `category` | `string` | required | Category directory (e.g., `"reports"`, `"realtime"`) |
368: | `operation` | `string` | required | Operation name (e.g., `"page_views"`) |
369: | `extraInfo` | `string` | `undefined` | Optional extra info for filename |
370: 
371: **Returns:** `string` — Full path to the saved file.


SOURCE skill/scripts/src/api/searchConsole.ts:1-175
1: /**
2:  * Search Console API - Google Search Console data retrieval
3:  */
4: 
5: import { getSearchConsoleClient, getSiteUrl } from '../core/client.js';
6: import { saveResult } from '../core/storage.js';
7: import { getSettings } from '../config/settings.js';
8: 
9: /**
10:  * Date range configuration for Search Console
11:  */
12: export interface SearchConsoleDateRange {
13:   startDate: string;
14:   endDate: string;
15: }
16: 
17: /**
18:  * Search analytics query options
19:  */
20: export interface SearchAnalyticsOptions {
21:   dimensions?: string[];
22:   dateRange?: string | SearchConsoleDateRange;
23:   rowLimit?: number;
24:   startRow?: number;
25:   save?: boolean;
26: }
27: 
28: /**
29:  * Search analytics row structure
30:  */
31: export interface SearchAnalyticsRow {
32:   keys: string[];
33:   clicks: number;
34:   impressions: number;
35:   ctr: number;
36:   position: number;
37: }
38: 
39: /**
40:  * Search analytics response structure
41:  */
42: export interface SearchAnalyticsResponse {
43:   rows?: SearchAnalyticsRow[];
44:   responseAggregationType?: string;
45: }
46: 
47: /**
48:  * Parse shorthand date range (e.g., "7d", "30d") to Search Console date format
49:  * Note: Search Console requires YYYY-MM-DD format, not GA4's "NdaysAgo" format
50:  */
51: export function parseSearchConsoleDateRange(range: string | SearchConsoleDateRange | undefined): SearchConsoleDateRange {
52:   if (!range) {
53:     const settings = getSettings();
54:     range = settings.defaultDateRange;
55:   }
56: 
57:   if (typeof range === 'object') {
58:     return range;
59:   }
60: 
61:   // Parse shorthand like "7d", "30d", "90d"
62:   const match = range.match(/^(\d+)d$/);
63:   if (match) {
64:     const days = parseInt(match[1], 10);
65:     const endDate = new Date();
66:     const startDate = new Date();
67:     startDate.setDate(startDate.getDate() - days);
68: 
69:     return {
70:       startDate: startDate.toISOString().split('T')[0],
71:       endDate: endDate.toISOString().split('T')[0],
72:     };
73:   }
74: 
75:   // Default to 30 days
76:   const endDate = new Date();
77:   const startDate = new Date();
78:   startDate.setDate(startDate.getDate() - 30);
79: 
80:   return {
81:     startDate: startDate.toISOString().split('T')[0],
82:     endDate: endDate.toISOString().split('T')[0],
83:   };
84: }
85: 
86: /**
87:  * Query search analytics data
88:  */
89: export async function querySearchAnalytics(options: SearchAnalyticsOptions): Promise<SearchAnalyticsResponse> {
90:   const {
91:     dimensions = ['query'],
92:     dateRange,
93:     rowLimit = 1000,
94:     startRow = 0,
95:     save = true,
96:   } = options;
97: 
98:   const client = getSearchConsoleClient();
99:   const siteUrl = getSiteUrl();
100:   const parsedDateRange = parseSearchConsoleDateRange(dateRange);
101: 
102:   const response = await client.searchanalytics.query({
103:     siteUrl,
104:     requestBody: {
105:       startDate: parsedDateRange.startDate,
106:       endDate: parsedDateRange.endDate,
107:       dimensions,
108:       rowLimit,
109:       startRow,
110:     },
111:   });
112: 
113:   const result = response.data as SearchAnalyticsResponse;
114: 
115:   if (save) {
116:     const operation = dimensions.join('_') || 'query';
117:     const extra = typeof dateRange === 'string' ? dateRange : undefined;
118:     saveResult(result, 'searchconsole', operation, extra);
119:   }
120: 
121:   return result;
122: }
123: 
124: /**
125:  * Get top search queries
126:  */
127: export async function getTopQueries(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
128:   return querySearchAnalytics({
129:     dimensions: ['query'],
130:     dateRange,
131:     rowLimit: 100,
132:   });
133: }
134: 
135: /**
136:  * Get top pages by search performance
137:  */
138: export async function getTopPages(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
139:   return querySearchAnalytics({
140:     dimensions: ['page'],
141:     dateRange,
142:     rowLimit: 100,
143:   });
144: }
145: 
146: /**
147:  * Get search performance by device type
148:  */
149: export async function getDevicePerformance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
150:   return querySearchAnalytics({
151:     dimensions: ['device'],
152:     dateRange,
153:   });
154: }
155: 
156: /**
157:  * Get search performance by country
158:  */
159: export async function getCountryPerformance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
160:   return querySearchAnalytics({
161:     dimensions: ['country'],
162:     dateRange,
163:     rowLimit: 50,
164:   });
165: }
166: 
167: /**
168:  * Get search appearance data (rich results, AMP, etc.)
169:  */
170: export async function getSearchAppearance(dateRange?: string | SearchConsoleDateRange): Promise<SearchAnalyticsResponse> {
171:   return querySearchAnalytics({
172:     dimensions: ['searchAppearance'],
173:     dateRange,
174:   });
175: }


SOURCE skill/scripts/src/config/settings.ts:1-74
1: /**
2:  * Settings Module - Environment configuration for GA4 API
3:  */
4: 
5: import { config } from 'dotenv';
6: import { join } from 'path';
7: 
8: // Load .env file from current working directory
9: config();
10: 
11: /**
12:  * Settings interface for GA4 API configuration
13:  */
14: export interface Settings {
15:   /** GA4 Property ID */
16:   propertyId: string;
17:   /** Service account email */
18:   clientEmail: string;
19:   /** Service account private key */
20:   privateKey: string;
21:   /** Default date range for reports (e.g., "30d", "7d") */
22:   defaultDateRange: string;
23:   /** Directory path for storing results */
24:   resultsDir: string;
25:   /** Search Console site URL (e.g., "https://example.com") */
26:   siteUrl: string;
27: }
28: 
29: /**
30:  * Validation result from validateSettings()
31:  */
32: export interface ValidationResult {
33:   valid: boolean;
34:   errors: string[];
35: }
36: 
37: /**
38:  * Get current settings from environment variables
39:  */
40: export function getSettings(): Settings {
41:   return {
42:     propertyId: process.env.GA4_PROPERTY_ID || '',
43:     clientEmail: process.env.GA4_CLIENT_EMAIL || '',
44:     privateKey: (process.env.GA4_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
45:     defaultDateRange: process.env.GA4_DEFAULT_DATE_RANGE || '30d',
46:     resultsDir: join(process.cwd(), 'results'),
47:     siteUrl: process.env.SEARCH_CONSOLE_SITE_URL || '',
48:   };
49: }
50: 
51: /**
52:  * Validate that all required settings are present
53:  */
54: export function validateSettings(): ValidationResult {
55:   const settings = getSettings();
56:   const errors: string[] = [];
57: 
58:   if (!settings.propertyId) {
59:     errors.push('GA4_PROPERTY_ID is required');
60:   }
61: 
62:   if (!settings.clientEmail) {
63:     errors.push('GA4_CLIENT_EMAIL is required');
64:   }
65: 
66:   if (!settings.privateKey) {
67:     errors.push('GA4_PRIVATE_KEY is required');
68:   }
69: 
70:   return {
71:     valid: errors.length === 0,
72:     errors,
73:   };
74: }


SOURCE skill/scripts/src/core/client.ts:1-133
1: /**
2:  * GA4 API Client - Singleton wrapper for BetaAnalyticsDataClient
3:  * Also includes Search Console and Indexing API clients
4:  */
5: 
6: import { BetaAnalyticsDataClient } from '@google-analytics/data';
7: import { searchconsole } from '@googleapis/searchconsole';
8: import { indexing } from '@googleapis/indexing';
9: import { google } from 'googleapis';
10: import { getSettings, validateSettings } from '../config/settings.js';
11: 
12: // Singleton client instances
13: let clientInstance: BetaAnalyticsDataClient | null = null;
14: let searchConsoleClientInstance: ReturnType<typeof searchconsole> | null = null;
15: let indexingClientInstance: ReturnType<typeof indexing> | null = null;
16: 
17: /**
18:  * Get the GA4 Analytics Data API client (singleton)
19:  *
20:  * @returns The BetaAnalyticsDataClient instance
21:  * @throws Error if credentials are invalid
22:  */
23: export function getClient(): BetaAnalyticsDataClient {
24:   if (clientInstance) {
25:     return clientInstance;
26:   }
27: 
28:   const validation = validateSettings();
29:   if (!validation.valid) {
30:     throw new Error(`Invalid GA4 credentials: ${validation.errors.join(', ')}`);
31:   }
32: 
33:   const settings = getSettings();
34: 
35:   clientInstance = new BetaAnalyticsDataClient({
36:     credentials: {
37:       client_email: settings.clientEmail,
38:       private_key: settings.privateKey,
39:     },
40:   });
41: 
42:   return clientInstance;
43: }
44: 
45: /**
46:  * Get the GA4 property ID formatted for API calls
47:  *
48:  * @returns Property ID with "properties/" prefix
49:  */
50: export function getPropertyId(): string {
51:   const settings = getSettings();
52:   return `properties/${settings.propertyId}`;
53: }
54: 
55: /**
56:  * Reset the client singleton (useful for testing)
57:  */
58: export function resetClient(): void {
59:   clientInstance = null;
60:   searchConsoleClientInstance = null;
61:   indexingClientInstance = null;
62: }
63: 
64: /**
65:  * Get Google Auth client for Search Console and Indexing APIs
66:  */
67: function getGoogleAuth() {
68:   const settings = getSettings();
69:   return new google.auth.GoogleAuth({
70:     credentials: {
71:       client_email: settings.clientEmail,
72:       private_key: settings.privateKey,
73:     },
74:     scopes: [
75:       'https://www.googleapis.com/auth/webmasters.readonly',
76:       'https://www.googleapis.com/auth/indexing',
77:     ],
78:   });
79: }
80: 
81: /**
82:  * Get the Search Console API client (singleton)
83:  *
84:  * @returns The Search Console client instance
85:  * @throws Error if credentials are invalid
86:  */
87: export function getSearchConsoleClient(): ReturnType<typeof searchconsole> {
88:   if (searchConsoleClientInstance) {
89:     return searchConsoleClientInstance;
90:   }
91: 
92:   const validation = validateSettings();
93:   if (!validation.valid) {
94:     throw new Error(`Invalid credentials: ${validation.errors.join(', ')}`);
95:   }
96: 
97:   const auth = getGoogleAuth();
98:   searchConsoleClientInstance = searchconsole({ version: 'v1', auth });
99: 
100:   return searchConsoleClientInstance;
101: }
102: 
103: /**
104:  * Get the Indexing API client (singleton)
105:  *
106:  * @returns The Indexing client instance
107:  * @throws Error if credentials are invalid
108:  */
109: export function getIndexingClient(): ReturnType<typeof indexing> {
110:   if (indexingClientInstance) {
111:     return indexingClientInstance;
112:   }
113: 
114:   const validation = validateSettings();
115:   if (!validation.valid) {
116:     throw new Error(`Invalid credentials: ${validation.errors.join(', ')}`);
117:   }
118: 
119:   const auth = getGoogleAuth();
120:   indexingClientInstance = indexing({ version: 'v3', auth });
121: 
122:   return indexingClientInstance;
123: }
124: 
125: /**
126:  * Get the Search Console site URL
127:  *
128:  * @returns Site URL from settings
129:  */
130: export function getSiteUrl(): string {
131:   const settings = getSettings();
132:   return settings.siteUrl;
133: }


SOURCE skill/scripts/src/core/storage.ts:1-171
1: /**
2:  * Storage Module - Auto-save results to JSON files with metadata
3:  */
4: 
5: import { existsSync, mkdirSync, writeFileSync, readFileSync, readdirSync } from 'fs';
6: import { join } from 'path';
7: import { getSettings } from '../config/settings.js';
8: 
9: /**
10:  * Metadata wrapper for saved results
11:  */
12: export interface ResultMetadata {
13:   savedAt: string;
14:   category: string;
15:   operation: string;
16:   propertyId: string;
17:   extraInfo?: string;
18: }
19: 
20: /**
21:  * Wrapped result with metadata
22:  */
23: export interface SavedResult<T = unknown> {
24:   metadata: ResultMetadata;
25:   data: T;
26: }
27: 
28: /**
29:  * Generate timestamp string for filenames: YYYYMMDD_HHMMSS
30:  */
31: function getTimestamp(): string {
32:   const now = new Date();
33:   const year = now.getFullYear();
34:   const month = String(now.getMonth() + 1).padStart(2, '0');
35:   const day = String(now.getDate()).padStart(2, '0');
36:   const hours = String(now.getHours()).padStart(2, '0');
37:   const minutes = String(now.getMinutes()).padStart(2, '0');
38:   const seconds = String(now.getSeconds()).padStart(2, '0');
39:   return `${year}${month}${day}_${hours}${minutes}${seconds}`;
40: }
41: 
42: /**
43:  * Sanitize string for use in filename
44:  */
45: function sanitizeFilename(str: string): string {
46:   return str.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase();
47: }
48: 
49: /**
50:  * Save result data to a JSON file with metadata wrapper
51:  *
52:  * @param data - The data to save
53:  * @param category - Category directory (e.g., 'reports', 'realtime')
54:  * @param operation - Operation name (e.g., 'page_views', 'traffic_sources')
55:  * @param extraInfo - Optional extra info for filename
56:  * @returns The full path to the saved file
57:  */
58: export function saveResult<T>(
59:   data: T,
60:   category: string,
61:   operation: string,
62:   extraInfo?: string
63: ): string {
64:   const settings = getSettings();
65:   const categoryDir = join(settings.resultsDir, category);
66: 
67:   // Ensure category directory exists
68:   if (!existsSync(categoryDir)) {
69:     mkdirSync(categoryDir, { recursive: true });
70:   }
71: 
72:   // Build filename
73:   const timestamp = getTimestamp();
74:   const sanitizedOperation = sanitizeFilename(operation);
75:   const sanitizedExtra = extraInfo ? `__${sanitizeFilename(extraInfo)}` : '';
76:   const filename = `${timestamp}__${sanitizedOperation}${sanitizedExtra}.json`;
77:   const filepath = join(categoryDir, filename);
78: 
79:   // Build wrapped result
80:   const result: SavedResult<T> = {
81:     metadata: {
82:       savedAt: new Date().toISOString(),
83:       category,
84:       operation,
85:       propertyId: settings.propertyId,
86:       ...(extraInfo && { extraInfo }),
87:     },
88:     data,
89:   };
90: 
91:   // Write to file
92:   writeFileSync(filepath, JSON.stringify(result, null, 2), 'utf-8');
93: 
94:   return filepath;
95: }
96: 
97: /**
98:  * Load a saved result from a JSON file
99:  *
100:  * @param filepath - Path to the JSON file
101:  * @returns The parsed result or null if file doesn't exist
102:  */
103: export function loadResult<T = unknown>(filepath: string): SavedResult<T> | null {
104:   if (!existsSync(filepath)) {
105:     return null;
106:   }
107: 
108:   try {
109:     const content = readFileSync(filepath, 'utf-8');
110:     return JSON.parse(content) as SavedResult<T>;
111:   } catch {
112:     return null;
113:   }
114: }
115: 
116: /**
117:  * List saved result files for a category
118:  *
119:  * @param category - Category to list results for
120:  * @param limit - Maximum number of results to return
121:  * @returns Array of file paths, sorted by date descending (newest first)
122:  */
123: export function listResults(category: string, limit?: number): string[] {
124:   const settings = getSettings();
125:   const categoryDir = join(settings.resultsDir, category);
126: 
127:   if (!existsSync(categoryDir)) {
128:     return [];
129:   }
130: 
131:   const files = readdirSync(categoryDir)
132:     .filter(f => f.endsWith('.json'))
133:     .map(f => join(categoryDir, f))
134:     .sort((a, b) => {
135:       // Sort by filename (which starts with timestamp) descending
136:       const nameA = a.split('/').pop() || '';
137:       const nameB = b.split('/').pop() || '';
138:       return nameB.localeCompare(nameA);
139:     });
140: 
141:   if (limit !== undefined) {
142:     return files.slice(0, limit);
143:   }
144: 
145:   return files;
146: }
147: 
148: /**
149:  * Get the most recent result for a category/operation
150:  *
151:  * @param category - Category to search
152:  * @param operation - Optional operation to filter by
153:  * @returns The most recent result or null
154:  */
155: export function getLatestResult<T = unknown>(
156:   category: string,
157:   operation?: string
158: ): SavedResult<T> | null {
159:   let files = listResults(category);
160: 
161:   if (operation) {
162:     const sanitized = sanitizeFilename(operation);
163:     files = files.filter(f => f.includes(`__${sanitized}`));
164:   }
165: 
166:   if (files.length === 0) {
167:     return null;
168:   }
169: 
170:   return loadResult<T>(files[0]);
171: }


SOURCE skill/scripts/src/index.ts:1-45
1: /**
2:  * GA4 Analytics Toolkit - Main Entry Point
3:  *
4:  * Simple interface for Google Analytics 4 data analysis.
5:  * All results are automatically saved to the /results directory with timestamps.
6:  *
7:  * Usage:
8:  *   import { siteOverview, trafficAnalysis } from './index.js';
9:  *   const overview = await siteOverview('30d');
10:  */
11: 
12: // Re-export all API functions
13: export * from './api/reports.js';
14: export * from './api/realtime.js';
15: export * from './api/metadata.js';
16: export * from './api/searchConsole.js';
17: export * from './api/indexing.js';
18: export * from './api/bulk-lookup.js';
19: 
20: // Re-export core utilities
21: export { getClient, getPropertyId, getSearchConsoleClient, getIndexingClient, getSiteUrl, resetClient } from './core/client.js';
22: export { saveResult, loadResult, listResults, getLatestResult } from './core/storage.js';
23: export { getSettings, validateSettings } from './config/settings.js';
24: 
25: // Import for orchestration functions
26: import {
27:   runReport,
28:   getPageViews,
29:   getTrafficSources,
30:   getUserDemographics,
31:   getEventCounts,
32:   getConversions,
33:   parseDateRange,
34:   type DateRange,
35: } from './api/reports.js';
36: import { getActiveUsers, getRealtimeEvents, getRealtimePages } from './api/realtime.js';
37: import { getPropertyMetadata } from './api/metadata.js';
38: import { saveResult } from './core/storage.js';
39: import {
40:   getTopQueries,
41:   getTopPages as getSearchConsoleTopPages,
42:   getDevicePerformance,
43:   getCountryPerformance,
44:   type SearchConsoleDateRange,
45: } from './api/searchConsole.js';


SOURCE skill/scripts/src/index.ts:278-296
278: /**
279:  * SEO page performance analysis
280:  */
281: export async function seoPagePerformance(dateRange?: string | SearchConsoleDateRange) {
282:   console.log('\n📄 Analyzing SEO page performance...');
283:   const results: Record<string, unknown> = {};
284: 
285:   console.log('  → Getting top pages by clicks...');
286:   results.topPages = await getSearchConsoleTopPages(dateRange);
287: 
288:   console.log('  → Getting country breakdown...');
289:   results.countryBreakdown = await getCountryPerformance(dateRange);
290: 
291:   const dateStr = typeof dateRange === 'string' ? dateRange : 'custom';
292:   saveResult(results, 'searchconsole', 'seo_page_performance', dateStr);
293: 
294:   console.log('✅ SEO page performance analysis complete\n');
295:   return results;
296: }


SOURCE skill/SKILL.md:1-158
1: ---
2: name: ga4-analytics
3: description: "Google Analytics 4, Search Console, and Indexing API toolkit. Analyze website traffic, page performance, user demographics, real-time visitors, search queries, and SEO metrics. Use when the user asks to: check site traffic, analyze page views, see traffic sources, view user demographics, get real-time visitor data, check search console queries, analyze SEO performance, request URL re-indexing, inspect index status, compare date ranges, check bounce rates, view conversion data, or get e-commerce revenue. Requires a Google Cloud service account with GA4 and Search Console access."
4: ---
5: 
6: # GA4 Analytics Toolkit
7: 
8: ## Setup
9: 
10: Install dependencies:
11: 
12: ```bash
13: cd scripts && npm install
14: ```
15: 
16: Configure credentials by creating a `.env` file in the project root:
17: 
18: ```
19: GA4_PROPERTY_ID=123456789
20: GA4_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
21: GA4_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
22: SEARCH_CONSOLE_SITE_URL=https://your-domain.com
23: GA4_DEFAULT_DATE_RANGE=30d
24: ```
25: 
26: **Prerequisites**: A Google Cloud project with the Analytics Data API, Search Console API, and Indexing API enabled. A service account with access to your GA4 property and Search Console.
27: 
28: ## Quick Start
29: 
30: | User says | Function to call |
31: |-----------|-----------------|
32: | "Show me site traffic for the last 30 days" | `siteOverview("30d")` |
33: | "What are my top search queries?" | `searchConsoleOverview("30d")` |
34: | "Who's on the site right now?" | `liveSnapshot()` |
35: | "Reindex these URLs" | `reindexUrls(["https://example.com/page1", ...])` |
36: | "Compare this month vs last month" | `compareDateRanges({startDate: "30daysAgo", endDate: "today"}, {startDate: "60daysAgo", endDate: "31daysAgo"})` |
37: | "What pages get the most traffic?" | `contentPerformance("30d")` |
38: 
39: Execute functions by importing from `scripts/src/index.ts`:
40: 
41: ```typescript
42: import { siteOverview, searchConsoleOverview } from './scripts/src/index.js';
43: 
44: const overview = await siteOverview('30d');
45: ```
46: 
47: Or run directly with tsx:
48: 
49: ```bash
50: npx tsx scripts/src/index.ts
51: ```
52: 
53: ## Workflow Pattern
54: 
55: Every analysis follows three phases:
56: 
57: ### 1. Analyze
58: Run API functions. Each call hits the Google APIs and returns structured data.
59: 
60: ### 2. Auto-Save
61: All results automatically save as timestamped JSON files to `results/{category}/`. File naming pattern: `YYYYMMDD_HHMMSS__operation__extra_info.json`
62: 
63: ### 3. Summarize
64: After analysis, read the saved JSON files and create a markdown summary in `results/summaries/` with data tables, trends, and recommendations.
65: 
66: ## High-Level Functions
67: 
68: ### GA4 Analytics
69: 
70: | Function | Purpose | What it gathers |
71: |----------|---------|----------------|
72: | `siteOverview(dateRange?)` | Comprehensive site snapshot | Page views, traffic sources, demographics, events |
73: | `trafficAnalysis(dateRange?)` | Traffic deep-dive | Sources, sessions by source/medium, new vs returning |
74: | `contentPerformance(dateRange?)` | Top pages analysis | Page views, landing pages, exit pages |
75: | `userBehavior(dateRange?)` | Engagement patterns | Demographics, events, daily engagement metrics |
76: | `compareDateRanges(range1, range2)` | Period comparison | Side-by-side metrics for two date ranges |
77: | `liveSnapshot()` | Real-time data | Active users, current pages, current events |
78: 
79: ### Search Console
80: 
81: | Function | Purpose | What it gathers |
82: |----------|---------|----------------|
83: | `searchConsoleOverview(dateRange?)` | SEO snapshot | Top queries, pages, device, country breakdown |
84: | `keywordAnalysis(dateRange?)` | Keyword deep-dive | Queries with device breakdown |
85: | `seoPagePerformance(dateRange?)` | Page SEO metrics | Top pages by clicks, country breakdown |
86: 
87: ### Indexing
88: 
89: | Function | Purpose |
90: |----------|---------|
91: | `reindexUrls(urls)` | Request re-indexing for multiple URLs |
92: | `checkIndexStatus(urls)` | Check if URLs are indexed |
93: 
94: ### Utility
95: 
96: | Function | Purpose |
97: |----------|---------|
98: | `getAvailableFields()` | List all available GA4 dimensions and metrics |
99: 
100: ### Individual API Functions
101: 
102: For granular control, import specific functions from the API modules. See [references/api-reference.md](references/api-reference.md) for the complete list of 30+ API functions with parameters, types, and examples.
103: 
104: ## Date Ranges
105: 
106: All functions accept flexible date range formats:
107: 
108: | Format | Example | Description |
109: |--------|---------|-------------|
110: | Shorthand | `"7d"`, `"30d"`, `"90d"` | Days ago to today |
111: | Explicit | `{startDate: "2024-01-01", endDate: "2024-01-31"}` | Specific dates |
112: | GA4 relative | `{startDate: "30daysAgo", endDate: "today"}` | GA4 relative format |
113: 
114: Default is `"30d"` (configurable via `GA4_DEFAULT_DATE_RANGE` in `.env`).
115: 
116: ## Results Storage
117: 
118: Results auto-save to `results/` with this structure:
119: 
120: ```
121: results/
122: ├── reports/          # GA4 standard reports
123: ├── realtime/         # Real-time snapshots
124: ├── searchconsole/    # Search Console data
125: ├── indexing/         # Indexing API results
126: └── summaries/        # Human-readable markdown summaries
127: ```
128: 
129: ### Managing Results
130: 
131: ```typescript
132: import { listResults, loadResult, getLatestResult } from './scripts/src/index.js';
133: 
134: // List recent results
135: const files = listResults('reports', 10);
136: 
137: // Load a specific result
138: const data = loadResult(files[0]);
139: 
140: // Get most recent result for an operation
141: const latest = getLatestResult('reports', 'site_overview');
142: ```
143: 
144: ## Common Dimensions and Metrics
145: 
146: ### Dimensions
147: `pagePath`, `pageTitle`, `sessionSource`, `sessionMedium`, `country`, `deviceCategory`, `browser`, `date`, `eventName`, `landingPage`, `newVsReturning`
148: 
149: ### Metrics
150: `screenPageViews`, `activeUsers`, `sessions`, `newUsers`, `bounceRate`, `averageSessionDuration`, `engagementRate`, `conversions`, `totalRevenue`, `eventCount`
151: 
152: ## Tips
153: 
154: 1. **Specify date ranges** — "last 7 days" or "last 90 days" gives different insights than the default 30 days
155: 2. **Request summaries** — After pulling data, ask for a markdown summary with tables and insights
156: 3. **Compare periods** — Use `compareDateRanges()` to spot trends (this month vs last month)
157: 4. **Check real-time data** — `liveSnapshot()` shows who's on the site right now
158: 5. **Combine GA4 + Search Console** — Traffic data plus search query data gives the full picture
