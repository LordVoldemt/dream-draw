import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import HomeView from "@/views/user/HomeView.vue";

const push = vi.fn();

vi.mock("vue-router", async () => {
  const actual = await vi.importActual<typeof import("vue-router")>("vue-router");

  return {
    ...actual,
    useRouter: () => ({
      push,
    }),
  };
});

const routerLinkStub = {
  props: ["to"],
  template: "<a><slot /></a>",
};

function mountHomeView() {
  return mount(HomeView, {
    global: {
      stubs: {
        RouterLink: routerLinkStub,
      },
    },
  });
}

describe("HomeView inspiration carousels", () => {
  beforeEach(() => {
    push.mockClear();
  });

  it("uses local project assets instead of remote placeholder images", () => {
    const wrapper = mountHomeView();

    const imageSources = wrapper
      .findAll("img")
      .map((image) => image.attributes("src") ?? "");

    expect(imageSources).not.toHaveLength(0);
    expect(imageSources.every((src) => !/^https?:\/\//.test(src))).toBe(true);
    expect(imageSources.every((src) => !src.includes("images.unsplash.com"))).toBe(true);
  });

  it("cycles the sword immortal image without opening the preset", async () => {
    const wrapper = mountHomeView();

    const image = wrapper.get('[data-testid="sword-immortal-image"]');
    expect(decodeURIComponent(image.attributes("src") ?? "")).toContain("女剑仙1");

    await wrapper.get('[data-testid="sword-immortal-next"]').trigger("click");

    expect(decodeURIComponent(image.attributes("src") ?? "")).toContain("女剑仙2");
    expect(push).not.toHaveBeenCalled();
  });

  it("cycles the changan noble image without opening the preset", async () => {
    const wrapper = mountHomeView();

    const image = wrapper.get('[data-testid="changan-noble-image"]');
    expect(decodeURIComponent(image.attributes("src") ?? "")).toContain("长安贵族千金1");

    await wrapper.get('[data-testid="changan-noble-next"]').trigger("click");

    expect(decodeURIComponent(image.attributes("src") ?? "")).toContain("长安贵族千金2");
    expect(push).not.toHaveBeenCalled();
  });
});
