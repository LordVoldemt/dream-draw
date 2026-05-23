import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import GenerateView from "@/views/user/GenerateView.vue";
import { useSessionStore } from "@/stores/session";

const polishPrompt = vi.fn();
const push = vi.fn();

vi.mock("@/api/dream-draw", async () => {
  const actual = await vi.importActual<typeof import("@/api/dream-draw")>("@/api/dream-draw");

  return {
    ...actual,
    DreamDrawApi: vi.fn().mockImplementation(() => ({
      polishPrompt,
      createTask: vi.fn(),
    })),
  };
});

vi.mock("vue-router", async () => {
  const actual = await vi.importActual<typeof import("vue-router")>("vue-router");

  return {
    ...actual,
    useRoute: () => ({ query: {} }),
    useRouter: () => ({
      push,
    }),
  };
});

function mountGenerateView() {
  setActivePinia(createPinia());
  const session = useSessionStore();
  session.setUserToken("user-token");

  return mount(GenerateView);
}

describe("GenerateView prompt polish", () => {
  beforeEach(() => {
    localStorage.clear();
    polishPrompt.mockReset();
    push.mockReset();
  });

  it("replaces the prompt with the polished result", async () => {
    polishPrompt.mockResolvedValue({
      prompt: "盛唐少女",
      polished_prompt: "盛唐贵族少女，金色步摇，红色齐胸襦裙，端庄华贵，柔和宫灯光影",
    });
    const wrapper = mountGenerateView();

    const textarea = wrapper.get("textarea");
    await textarea.setValue("盛唐少女");
    await wrapper.get('[data-testid="polish-prompt"]').trigger("click");
    await flushPromises();

    expect(polishPrompt).toHaveBeenCalledWith("盛唐少女");
    expect((textarea.element as HTMLTextAreaElement).value).toBe(
      "盛唐贵族少女，金色步摇，红色齐胸襦裙，端庄华贵，柔和宫灯光影",
    );
    expect(wrapper.text()).toContain("Prompt 已润色");
  });

  it("shows a recoverable message when polishing fails", async () => {
    polishPrompt.mockRejectedValue(new Error("润色服务暂不可用"));
    const wrapper = mountGenerateView();

    await wrapper.get("textarea").setValue("仙侠白衣少女");
    await wrapper.get('[data-testid="polish-prompt"]').trigger("click");
    await flushPromises();

    expect(wrapper.text()).toContain("润色服务暂不可用");
  });
});
