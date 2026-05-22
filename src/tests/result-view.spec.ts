import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ResultView from "@/views/user/ResultView.vue";

const push = vi.fn();
const getWorkDetail = vi.fn();
const getWorkDetailByTask = vi.fn();
const getTaskDetail = vi.fn();
const favoriteWork = vi.fn();
const unfavoriteWork = vi.fn();
const shareWork = vi.fn();

vi.mock("vue-router", async () => {
  const actual = await vi.importActual<typeof import("vue-router")>("vue-router");

  return {
    ...actual,
    useRoute: () => ({
      params: { id: "19" },
    }),
    useRouter: () => ({
      push,
    }),
  };
});

vi.mock("@/stores/session", () => ({
  useSessionStore: () => ({
    userToken: "token",
  }),
}));

vi.mock("@/api/dream-draw", () => ({
  DreamDrawApi: class {
    getWorkDetail = getWorkDetail;
    getWorkDetailByTask = getWorkDetailByTask;
    getTaskDetail = getTaskDetail;
    favoriteWork = favoriteWork;
    unfavoriteWork = unfavoriteWork;
    shareWork = shareWork;
  },
}));

const workPayload = {
  work: {
    id: 19,
    image_url: "/uploads/works/task-19.png",
    prompt_snapshot: "盛唐时期丰腴贵族女子",
    style_id: "style_tang_dynasty",
    template_id: "tpl_oc_avatar",
    ratio_id: "ratio_square_1_1",
    quality_level: "standard",
    reference_mode: null,
    reference_image_count: 0,
    final_points: 1,
    is_favorite: false,
  },
};

function mountResultView() {
  return mount(ResultView);
}

describe("ResultView download action", () => {
  beforeEach(() => {
    push.mockReset();
    getWorkDetail.mockReset();
    getWorkDetailByTask.mockReset();
    getTaskDetail.mockReset();
    favoriteWork.mockReset();
    unfavoriteWork.mockReset();
    shareWork.mockReset();
    getWorkDetail.mockResolvedValue(workPayload);
  });

  it("downloads the original image file when clicking download", async () => {
    const nativeCreateElement = document.createElement.bind(document);
    const appendChild = vi.spyOn(document.body, "appendChild");
    const createElement = vi.spyOn(document, "createElement").mockImplementation((tagName: string) => {
      const element = nativeCreateElement(tagName);
      if (tagName === "a") {
        element.click = vi.fn();
        element.remove = vi.fn();
      }
      return element;
    });

    const wrapper = mountResultView();
    await flushPromises();

    await wrapper.get(".primary-action").trigger("click");

    expect(createElement).toHaveBeenCalledWith("a");
    expect(appendChild).toHaveBeenCalled();
    const anchor = appendChild.mock.calls[0][0] as HTMLAnchorElement;
    expect(anchor.href).toContain("/uploads/works/task-19.png");
    expect(anchor.download).toBe("dream-draw-19.png");
    expect(anchor.click).toHaveBeenCalled();
    expect(anchor.remove).toHaveBeenCalled();

    createElement.mockRestore();
    appendChild.mockRestore();
  });
});
