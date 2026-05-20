import catalogData from "../../shared/product-catalog.json";
import { modelStatuses, qualityLevels, ratios, styles, taskStatuses, templates } from "@/shared/catalog";

describe("product catalog", () => {
  it("covers all required style enums", () => {
    expect(styles.map((item) => item.id)).toEqual(
      catalogData.styles.map((item) => item.id),
    );
  });

  it("covers all required template enums", () => {
    expect(templates.map((item) => item.id)).toEqual(
      catalogData.templates.map((item) => item.id),
    );
  });

  it("covers all required ratio enums", () => {
    expect(ratios.map((item) => item.id)).toEqual(
      catalogData.ratios.map((item) => item.id),
    );
  });

  it("covers all required quality and status enums", () => {
    expect(qualityLevels.map((item) => item.id)).toEqual(
      catalogData.qualityLevels.map((item) => item.id),
    );
    expect(modelStatuses).toEqual(catalogData.modelStatuses);
    expect(taskStatuses).toEqual(catalogData.taskStatuses);
  });
});
