import { describe, expect, it } from "vitest";
import { shortenCwd } from "../extension.js";

describe("shortenCwd", () => {
	it("keeps the leaf and immediate parent full, abbreviates the rest", () => {
		expect(shortenCwd("~/Developer/_SketchUp/sbd-legionrepo-wt/snowflake_cdp_dcm/projects/snowflake_cdp_dcm")).toBe(
			"~/D/_S/s/s/projects/snowflake_cdp_dcm",
		);
	});

	it("leaves short paths untouched", () => {
		expect(shortenCwd("~/projects/dotfiles")).toBe("~/projects/dotfiles");
		expect(shortenCwd("~")).toBe("~");
		expect(shortenCwd("/")).toBe("/");
	});

	it("handles absolute paths outside $HOME", () => {
		expect(shortenCwd("/var/www/some-very-long-service-name/backend/src")).toBe("/v/w/s/backend/src");
	});

	it("falls back to keeping 1 segment, then hard-truncates with an ellipsis, once over maxLen", () => {
		const deep = "~/Developer/_SketchUp/sbd-legionrepo-wt/snowflake_cdp_dcm/projects/snowflake_cdp_dcm";
		expect(shortenCwd(deep, 30)).toBe("~/D/_S/s/s/p/snowflake_cdp_dcm");
		expect(shortenCwd(deep, 20).startsWith("…")).toBe(true);
		expect(shortenCwd(deep, 20).endsWith("snowflake_cdp_dcm")).toBe(true);
	});
});
