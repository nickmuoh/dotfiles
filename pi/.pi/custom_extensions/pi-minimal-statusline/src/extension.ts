// Shortens the footer's working-directory line: keeps the leaf and its
// immediate parent full, abbreviates every earlier segment to its first
// char (plus one more char if that first char isn't a letter/digit, e.g.
// `_SketchUp` -> `_S`), and hard-caps the whole line at MAX_LEN.
//
// Replaces Pi's footer via ctx.ui.setFooter and rebuilds the second line
// (token stats / cost / context% / model / effort) from public
// ExtensionContext data so it matches the stock footer's format.
//
// ponytail: no responsive width truncation/wrapping like the stock footer
// (truncateToWidth). On very narrow terminals the line may overflow instead
// of wrapping. Add truncateToWidth from @earendil-works/pi-tui if that bites.
// ponytail: the "(sub)" subscription-cost flag needs session.modelRuntime,
// which isn't exposed to extensions; approximated via provider === "kimi-coding"
// only. Upgrade if other subscription providers need the flag.
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const MAX_LEN = 80;

// Inlined: formatCwdForFooter/formatTokens/usage-totals aren't in the
// package's public API (only in its internal CLI bundle), so these tiny
// helpers are reimplemented rather than imported.
function formatCwdForFooter(cwd: string, home: string | undefined): string {
	if (!home) return cwd;
	if (cwd === home) return "~";
	return cwd.startsWith(`${home}/`) ? `~${cwd.slice(home.length)}` : cwd;
}

function formatTokens(count: number): string {
	if (count < 1000) return String(count);
	if (count < 10000) return `${(count / 1000).toFixed(1)}k`;
	if (count < 1000000) return `${Math.round(count / 1000)}k`;
	if (count < 10000000) return `${(count / 1000000).toFixed(1)}M`;
	return `${Math.round(count / 1000000)}M`;
}

function abbreviateSegment(seg: string): string {
	const first = seg[0];
	if (/[a-zA-Z0-9]/.test(first)) return first;
	const next = seg.slice(1).match(/[a-zA-Z0-9]/);
	return next ? first + next[0] : first;
}

function shorten(pwd: string, keepLast: number): string {
	const isHome = pwd.startsWith("~");
	const segs = pwd.split("/").filter(Boolean);
	const real = isHome ? segs.slice(1) : segs;
	if (real.length <= keepLast) return pwd;
	const kept = real.slice(-keepLast);
	const abbrev = real.slice(0, -keepLast).map(abbreviateSegment);
	const prefix = isHome ? "~" : pwd.startsWith("/") ? "" : "";
	return [prefix, ...abbrev, ...kept].join("/") || "/";
}

export function shortenCwd(pwd: string, maxLen = MAX_LEN): string {
	let out = shorten(pwd, 2);
	if (out.length <= maxLen) return out;
	out = shorten(pwd, 1);
	if (out.length <= maxLen) return out;
	return maxLen <= 1 ? out.slice(-maxLen) : `…${out.slice(-(maxLen - 1))}`;
}

function renderFooter(
	ctx: ExtensionContext,
	theme: { fg(color: string, text: string): string },
	footerData: { getGitBranch(): string | null; getAvailableProviderCount(): number },
) {
	const home = process.env.HOME || process.env.USERPROFILE;
	let pwd = shortenCwd(formatCwdForFooter(ctx.sessionManager.getCwd(), home));
	const branch = footerData.getGitBranch();
	if (branch) pwd += ` (${branch})`;
	const sessionName = ctx.sessionManager.getSessionName();
	if (sessionName) pwd += ` • ${sessionName}`;

	const usageTotals = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, cost: 0 };
	const addUsage = (usage: { input: number; output: number; cacheRead: number; cacheWrite: number; cost?: { total: number } }) => {
		usageTotals.input += usage.input;
		usageTotals.output += usage.output;
		usageTotals.cacheRead += usage.cacheRead;
		usageTotals.cacheWrite += usage.cacheWrite;
		usageTotals.cost += usage.cost?.total ?? 0;
	};
	let latestCacheHitRate: number | undefined;
	for (const entry of ctx.sessionManager.getEntries()) {
		if (entry.type === "message" && entry.message.role === "assistant") {
			addUsage(entry.message.usage);
			const prompt = entry.message.usage.input + entry.message.usage.cacheRead + entry.message.usage.cacheWrite;
			latestCacheHitRate = prompt > 0 ? (entry.message.usage.cacheRead / prompt) * 100 : undefined;
		} else if (entry.type === "message" && entry.message.role === "toolResult" && entry.message.usage) {
			addUsage(entry.message.usage);
		} else if ((entry.type === "branch_summary" || entry.type === "compaction") && entry.usage) {
			addUsage(entry.usage);
		}
	}

	const contextUsage = ctx.getContextUsage();
	const contextWindow = contextUsage?.contextWindow ?? ctx.model?.contextWindow ?? 0;
	const contextPercent = contextUsage?.percent != null ? contextUsage.percent.toFixed(1) : "?";

	const stats: string[] = [];
	if (usageTotals.input) stats.push(`↑${formatTokens(usageTotals.input)}`);
	if (usageTotals.output) stats.push(`↓${formatTokens(usageTotals.output)}`);
	if (usageTotals.cacheRead) stats.push(`R${formatTokens(usageTotals.cacheRead)}`);
	if (usageTotals.cacheWrite) stats.push(`W${formatTokens(usageTotals.cacheWrite)}`);
	if (latestCacheHitRate !== undefined) stats.push(`CH${latestCacheHitRate.toFixed(1)}%`);
	const usingSubscription = ctx.model?.provider === "kimi-coding";
	if (usageTotals.cost || usingSubscription) stats.push(`$${usageTotals.cost.toFixed(3)}${usingSubscription ? " (sub)" : ""}`);
	stats.push(contextUsage?.percent != null ? `${contextPercent}%/${formatTokens(contextWindow)}` : `?/${formatTokens(contextWindow)}`);

	let rightSide = ctx.model?.id || "no-model";
	if (ctx.model?.reasoning) rightSide += ` • ${ctx.thinkingLevel || "off"}`;
	if (footerData.getAvailableProviderCount() > 1 && ctx.model) rightSide = `(${ctx.model.provider}) ${rightSide}`;

	return [theme.fg("dim", pwd), theme.fg("dim", `${stats.join(" ")}   ${rightSide}`)];
}

export default function piMinimalStatuslineExtension(pi: ExtensionAPI) {
	pi.on("session_start", (_event, ctx) => {
		if (!ctx.hasUI) return;
		ctx.ui.setFooter((_tui, theme, footerData) => ({
			render: (_width: number) => renderFooter(ctx, theme, footerData),
			invalidate: () => {},
		}));
	});
}
