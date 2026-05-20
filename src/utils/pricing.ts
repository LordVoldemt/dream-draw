import { qualityLevels, ratios, styles, templates } from "@/shared/catalog";

export interface QuotePreview {
  basePoints: number;
  styleExtraPoints: number;
  templateExtraPoints: number;
  ratioExtraPoints: number;
  referenceImageExtraPoints: number;
  finalPoints: number;
}

export function getPromptLengthState(prompt: string) {
  const length = prompt.trim().length;
  if (length === 0) {
    return "empty";
  }
  if (length <= 40) {
    return "prompt_short";
  }
  if (length <= 120) {
    return "prompt_standard";
  }
  if (length <= 300) {
    return "prompt_long";
  }
  return "prompt_over_limit";
}

export function buildQuotePreview(input: {
  styleId: string;
  templateId: string;
  ratioId: string;
  qualityLevel: string;
  referenceImageCount: number;
}): QuotePreview {
  const style = styles.find((item) => item.id === input.styleId);
  const template = templates.find((item) => item.id === input.templateId);
  const ratio = ratios.find((item) => item.id === input.ratioId);
  const quality = qualityLevels.find((item) => item.id === input.qualityLevel);

  const basePoints = quality?.basePoints ?? 1;
  const styleExtraPoints = style?.extraPoints ?? 0;
  const templateExtraPoints = template?.extraPoints ?? 0;
  const ratioExtraPoints = ratio?.extraPoints ?? 0;
  const referenceImageExtraPoints = Math.max(0, Math.min(3, input.referenceImageCount));

  return {
    basePoints,
    styleExtraPoints,
    templateExtraPoints,
    ratioExtraPoints,
    referenceImageExtraPoints,
    finalPoints:
      basePoints +
      styleExtraPoints +
      templateExtraPoints +
      ratioExtraPoints +
      referenceImageExtraPoints,
  };
}
