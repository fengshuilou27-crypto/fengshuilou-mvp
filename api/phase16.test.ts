// Phase 16 測試：URL 正規化、多專家標題匹配、手動錄入 async job 校驗層
// 注意：唔准真寫 public/data——dryRun 只測校驗層（無效輸入同步拒絕、唔建行），唔觸碰 DB/檔案。
import { describe, it, expect } from "vitest";
import {
  parseVideoId, canonicalVideoUrl,
  EXPERT_TITLE_MATCH, matchExpertByTitle,
  submitManualView, getManualViewJob,
} from "./pipeline";

describe("parseVideoId 各形態", () => {
  it("youtu.be 短鏈 + si 追蹤參數", () => {
    expect(parseVideoId("https://youtu.be/ZUJL2tOnpJU?si=f8HoPFYNVY8tuq7r")).toBe("ZUJL2tOnpJU");
  });
  it("youtu.be 短鏈 + 尾 `?`", () => {
    expect(parseVideoId("https://youtu.be/ZUJL2tOnpJU?")).toBe("ZUJL2tOnpJU");
    expect(parseVideoId("https://youtu.be/ZUJL2tOnpJU")).toBe("ZUJL2tOnpJU");
  });
  it("watch?v= 形態（含額外參數前後）", () => {
    expect(parseVideoId("https://www.youtube.com/watch?v=ZUJL2tOnpJU")).toBe("ZUJL2tOnpJU");
    expect(parseVideoId("https://www.youtube.com/watch?v=ZUJL2tOnpJU&t=120s")).toBe("ZUJL2tOnpJU");
    expect(parseVideoId("https://www.youtube.com/watch?t=5&v=ZUJL2tOnpJU")).toBe("ZUJL2tOnpJU");
  });
  it("shorts / live 形態", () => {
    expect(parseVideoId("https://www.youtube.com/shorts/ZUJL2tOnpJU")).toBe("ZUJL2tOnpJU");
    expect(parseVideoId("https://www.youtube.com/live/ZUJL2tOnpJU?si=abc")).toBe("ZUJL2tOnpJU");
  });
  it("裸 videoId", () => {
    expect(parseVideoId("ZUJL2tOnpJU")).toBe("ZUJL2tOnpJU");
    expect(parseVideoId("  ZUJL2tOnpJU  ")).toBe("ZUJL2tOnpJU");
  });
  it("垃圾輸入回 null", () => {
    expect(parseVideoId("")).toBe(null);
    expect(parseVideoId("hello world")).toBe(null);
    expect(parseVideoId("https://example.com/watch?v=ZUJL2tOnpJU")).toBe(null); // 非 youtube 域名
    expect(parseVideoId("https://youtu.be/short")).toBe(null); // 唔夠 11 位
    expect(parseVideoId("https://www.youtube.com/watch?v=")).toBe(null);
  });
});

describe("canonicalVideoUrl", () => {
  it("youtu.be 短鏈歸一為 canonical watch URL", () => {
    expect(canonicalVideoUrl("https://youtu.be/ZUJL2tOnpJU?si=f8HoPFYNVY8tuq7r"))
      .toBe("https://www.youtube.com/watch?v=ZUJL2tOnpJU");
  });
  it("watch/shorts 形態同樣歸一", () => {
    expect(canonicalVideoUrl("https://www.youtube.com/watch?v=ZUJL2tOnpJU&t=9"))
      .toBe("https://www.youtube.com/watch?v=ZUJL2tOnpJU");
    expect(canonicalVideoUrl("https://www.youtube.com/shorts/ZUJL2tOnpJU"))
      .toBe("https://www.youtube.com/watch?v=ZUJL2tOnpJU");
  });
  it("非 YouTube URL 回 trim 後原串；空輸入回空串", () => {
    expect(canonicalVideoUrl("  https://example.com/article  ")).toBe("https://example.com/article");
    expect(canonicalVideoUrl(undefined)).toBe("");
    expect(canonicalVideoUrl("")).toBe("");
  });
});

describe("EXPERT_TITLE_MATCH 多專家標題匹配", () => {
  it("命中：繁體", () => {
    expect(matchExpertByTitle("洪灝：美股下半年點睇")?.expertId).toBe("hong");
    expect(matchExpertByTitle("【專訪】蔡金強談半導體週期")?.expertId).toBe("choi");
    expect(matchExpertByTitle("譚新強 拆解港股")?.expertId).toBe("tam");
    expect(matchExpertByTitle("林本利教授講樓市")?.expertId).toBe("lam");
    expect(matchExpertByTitle("林一鳴：債券配置")?.expertId).toBe("lamy");
    expect(matchExpertByTitle("莊太量談香港經濟")?.expertId).toBe("chong");
    expect(matchExpertByTitle("許佳龍談加密監管")?.expertId).toBe("hui");
    expect(matchExpertByTitle("Jurrien Timmer on markets")?.expertId).toBe("timmer");
    expect(matchExpertByTitle("Fidelity's Timmer says...")?.expertId).toBe("timmer"); // i flag
  });
  it("命中：簡體變體", () => {
    expect(matchExpertByTitle("洪灏最新观点")?.expertId).toBe("hong");
    expect(matchExpertByTitle("蔡金强：黄金还买不买")?.expertId).toBe("choi");
    expect(matchExpertByTitle("谭新强访谈")?.expertId).toBe("tam");
    expect(matchExpertByTitle("林一鸣聊美股")?.expertId).toBe("lamy");
    expect(matchExpertByTitle("庄太量点评")?.expertId).toBe("chong");
    expect(matchExpertByTitle("许佳龙专访")?.expertId).toBe("hui");
  });
  it("唔命中回 null", () => {
    expect(matchExpertByTitle("今日大市回顧")).toBe(null);
    expect(matchExpertByTitle("")).toBe(null);
    expect(matchExpertByTitle("林氏兄弟談投資")).toBe(null); // 姓相同唔算命中
  });
  it("有序首命中即停（洪灝排蔡金強前）", () => {
    expect(EXPERT_TITLE_MATCH[0][1].expertId).toBe("hong");
    expect(EXPERT_TITLE_MATCH[1][1].expertId).toBe("choi");
  });
});

describe("submitManualView 校驗層（同步，唔建行/唔寫檔）", () => {
  const longContent = "呢段係夠長嘅字幕內容。".repeat(20); // >100 字
  it("專家名空 → ok:false 即拒", () => {
    const r = submitManualView({ expertName: "  ", title: "t", content: longContent });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error).toContain("專家名");
  });
  it("標題空 → ok:false 即拒", () => {
    const r = submitManualView({ expertName: "洪灝", title: "", content: longContent });
    expect(r.ok).toBe(false);
  });
  it("內容少於 100 字 → ok:false 即拒（dryRun 都一樣拒）", () => {
    const r = submitManualView({ expertName: "洪灝", title: "t", content: "太短", dryRun: true });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error).toContain("100 字");
  });
  it("合法輸入 → 同步回 { ok:true, jobId }，job 狀態即時可查（running）", () => {
    // dryRun=true：即使背景 job 行完都唔會寫 DB/檔案（DB 唔通時 job 會 failed，唔影響斷言）
    const r = submitManualView({ expertName: "洪灝", title: "測試觀點", content: longContent, dryRun: true });
    expect(r.ok).toBe(true);
    if (r.ok) {
      expect(r.jobId.length).toBeGreaterThanOrEqual(8);
      const j = getManualViewJob(r.jobId);
      expect(["running", "done", "failed"]).toContain(j.status); // 背景執行中/已完成皆合法
    }
  });
  it("未知 jobId → status unknown", () => {
    expect(getManualViewJob("00000000-0000-0000-0000-000000000000").status).toBe("unknown");
  });
});
