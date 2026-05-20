import catalogData from "../../shared/product-catalog.json";

export type StyleCatalogItem = {
  id: string;
  name: string;
  description: string;
  extraPoints: number;
  keywords: string[];
};

export type TemplateCatalogItem = {
  id: string;
  name: string;
  scene: string;
  composition: string;
  extraPoints: number;
};

export type RatioCatalogItem = {
  id: string;
  label: string;
  title: string;
  scene: string;
  resolution: string;
  extraPoints: number;
};

export type QualityCatalogItem = {
  id: string;
  name: string;
  basePoints: number;
};

export const productCatalog = catalogData;
export const styles = catalogData.styles as StyleCatalogItem[];
export const templates = catalogData.templates as TemplateCatalogItem[];
export const ratios = catalogData.ratios as RatioCatalogItem[];
export const qualityLevels = catalogData.qualityLevels as QualityCatalogItem[];
export const modelStatuses = catalogData.modelStatuses as string[];
export const taskStatuses = catalogData.taskStatuses as string[];
export const referenceImageModes = catalogData.referenceImageModes as Array<{
  id: string;
  name: string;
}>;
