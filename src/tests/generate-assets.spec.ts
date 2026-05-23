import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import GenerateView from "@/views/user/GenerateView.vue";

vi.mock("vue-router", async () => {
  const actual = await vi.importActual<typeof import("vue-router")>("vue-router");

  return {
    ...actual,
    useRoute: () => ({ query: {} }),
    useRouter: () => ({
      push: vi.fn(),
    }),
  };
});

function mountGenerateView() {
  setActivePinia(createPinia());

  return mount(GenerateView);
}

describe("GenerateView image assets", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("uses local project assets instead of remote placeholder images", () => {
    const wrapper = mountGenerateView();

    const imageSources = wrapper
      .findAll("img")
      .map((image) => image.attributes("src") ?? "");

    expect(imageSources).not.toHaveLength(0);
    expect(imageSources.every((src) => !/^https?:\/\//.test(src))).toBe(true);
    expect(imageSources.every((src) => !src.includes("images.unsplash.com"))).toBe(true);
  });
});
