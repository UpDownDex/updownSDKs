import { describe, expect, it } from "vitest";

import { bigMath } from "../src/utils/bigmath";
import { expandDecimals, formatAmount, parseValue } from "../src/utils/numbers";

describe("Utility Functions", () => {
  describe("bigMath", () => {
    it("should handle edge cases", () => {
      expect(bigMath.max(0n, 0n)).toBe(0n);
      expect(bigMath.min(0n, 0n)).toBe(0n);
      expect(bigMath.abs(0n)).toBe(0n);
    });
  });

  describe("numbers", () => {
    it("should handle zero values", () => {
      expect(expandDecimals(0n, 18)).toBe(0n);
      expect(parseValue("0", 18)).toBe(0n);
      expect(formatAmount(0n, 18, 2)).toBe("0.00");
    });

    it("should handle very small values", () => {
      const small = expandDecimals(1n, 18);
      expect(formatAmount(small, 18, 18)).toBe("0.000000000000000001");
    });
  });
});
