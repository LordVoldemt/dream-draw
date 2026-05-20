import { buildQuotePreview, getPromptLengthState } from "@/utils/pricing";

describe("pricing helpers", () => {
  it("computes quote preview from catalog enums", () => {
    expect(
      buildQuotePreview({
        styleId: "style_tang_dynasty",
        templateId: "tpl_dreamgirl_portrait",
        ratioId: "ratio_square_1_1",
        qualityLevel: "hd",
        referenceImageCount: 2,
      }),
    ).toEqual({
      basePoints: 2,
      styleExtraPoints: 1,
      templateExtraPoints: 1,
      ratioExtraPoints: 0,
      referenceImageExtraPoints: 2,
      finalPoints: 6,
    });
  });

  it("maps prompt length states according to ux rules", () => {
    expect(getPromptLengthState("a")).toBe("prompt_short");
    expect(getPromptLengthState("a".repeat(50))).toBe("prompt_standard");
    expect(getPromptLengthState("a".repeat(180))).toBe("prompt_long");
    expect(getPromptLengthState("a".repeat(301))).toBe("prompt_over_limit");
  });
});
