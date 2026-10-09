// Phase 19 修復測試：kome 死通道誠實化、kimiChat 抗 TCP reset（streaming + 重試）、
// manual view job watchdog 終態保證、netCheck kome 真實探針。
// 全部 mock fetch / mock runner——唔掂真網絡、唔掂 DB、唔含任何真實 key（安全紅線）。
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  getTranscriptViaKome, kimiChat, netCheck,
  submitManualView, getManualViewJob, _setManualViewRunnerForTest,
} from "./pipeline";

const SSE_HEADERS = { "content-type": "text/event-stream" };

function sseResponse(chunks: string[]): Response {
  const body = chunks.map(c => `data: ${c}\n\n`).join("") + "data: [DONE]\n\n";
  return new Response(body, { status: 200, headers: SSE_HEADERS });
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  _setManualViewRunnerForTest(null);
  delete process.env.MANUAL_VIEW_JOB_TIMEOUT_MS;
});

describe("getTranscriptViaKome 死通道誠實化", () => {
  it("403 + Vercel Security Checkpoint HTML → reason 含「封鎖」", async () => {
    const html = `<!DOCTYPE html><html><head><title>Vercel Security Checkpoint</title></head><body>...</body></html>`;
    vi.mocked(fetch).mockResolvedValue(new Response(html, { status: 403, headers: { "content-type": "text/html" } }));
    const r = await getTranscriptViaKome("dQw4w9WgXcQ");
    expect(r.text).toBeNull();
    expect(r.reason).toMatch(/封鎖|失效/);
  });

  it("HTTP 429 → reason 含「付費」/「429」", async () => {
    vi.mocked(fetch).mockResolvedValue(new Response("Too Many Requests", { status: 429 }));
    const r = await getTranscriptViaKome("dQw4w9WgXcQ");
    expect(r.text).toBeNull();
    expect(r.reason).toMatch(/付費|429/);
  });

  it("200 但 transcript 係「aren't available」英文錯誤句 → reason 係發佈者停用字幕", async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(
      JSON.stringify({ transcript: "Transcripts aren't available for this video." }),
      { status: 200, headers: { "content-type": "application/json" } }));
    const r = await getTranscriptViaKome("dQw4w9WgXcQ");
    expect(r.text).toBeNull();
    expect(r.reason).toMatch(/冇可用字幕/);
  });

  it("網絡 throw → reason 係「字幕代理連接失敗」", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("fetch failed"));
    const r = await getTranscriptViaKome("dQw4w9WgXcQ");
    expect(r.text).toBeNull();
    expect(r.reason).toMatch(/字幕代理連接失敗/);
  });
});

describe("kimiChat 抗 TCP reset", () => {
  it("連續 2 次 fetch failed → 第 3 次 SSE stream 成功，累積 delta.content，共 3 次嘗試", async () => {
    const m = vi.mocked(fetch);
    m.mockRejectedValueOnce(new TypeError("fetch failed"));
    m.mockRejectedValueOnce(new TypeError("fetch failed"));
    m.mockResolvedValueOnce(sseResponse([
      JSON.stringify({ choices: [{ delta: { content: '{"summary":' } }] }),
      JSON.stringify({ choices: [{ delta: { content: '"x"}' } }] }),
    ]));
    const out = await kimiChat({ model: "kimi-k2.6", prompt: "test", jsonMode: true });
    expect(out).toBe('{"summary":"x"}');
    expect(m).toHaveBeenCalledTimes(3);
  }, 15000);

  it("SSE 忽略 reasoning_content，只累積 content", async () => {
    vi.mocked(fetch).mockResolvedValue(sseResponse([
      JSON.stringify({ choices: [{ delta: { reasoning_content: "諗緊…" } }] }),
      JSON.stringify({ choices: [{ delta: { content: "答案" } }] }),
    ]));
    const out = await kimiChat({ model: "kimi-k2.6", prompt: "test" });
    expect(out).toBe("答案");
  });

  it("HTTP 400 + jsonMode → 唔帶 response_format、唔帶 stream 非 stream 重試一次", async () => {
    const m = vi.mocked(fetch);
    m.mockResolvedValueOnce(new Response("bad request", { status: 400 }));
    m.mockResolvedValueOnce(new Response(
      JSON.stringify({ choices: [{ message: { content: '{"summary":"ok"}' } }] }),
      { status: 200, headers: { "content-type": "application/json" } }));
    const out = await kimiChat({ model: "kimi-k2.6", prompt: "test", jsonMode: true });
    expect(out).toBe('{"summary":"ok"}');
    expect(m).toHaveBeenCalledTimes(2);
    const secondBody = JSON.parse(String(m.mock.calls[1][1]?.body));
    expect(secondBody.response_format).toBeUndefined();
    expect(secondBody.stream).toBeUndefined();
  });

  it("HTTP 404 → throw code=404（caller 跳下一個模型），唔重試", async () => {
    const m = vi.mocked(fetch);
    m.mockResolvedValue(new Response("not found", { status: 404 }));
    await expect(kimiChat({ model: "kimi-k2.6", prompt: "test" })).rejects.toMatchObject({ code: 404 });
    expect(m).toHaveBeenCalledTimes(1);
  });

  it("欠費 body（suspended/insufficient balance）→ 人話錯誤", async () => {
    vi.mocked(fetch).mockResolvedValue(new Response('{"error":"account suspended: insufficient balance"}', { status: 429 }));
    await expect(kimiChat({ model: "kimi-k2.6", prompt: "test" })).rejects.toThrow(/餘額不足已被暫停/);
  });

  it("stream 完成但 content 為空 → 非 stream fallback 一次（reasoning 耗盡 max_tokens 情境）", async () => {
    const m = vi.mocked(fetch);
    m.mockResolvedValueOnce(sseResponse([JSON.stringify({ choices: [{ delta: { reasoning_content: "齋諗唔答" } }] })]));
    m.mockResolvedValueOnce(new Response(
      JSON.stringify({ choices: [{ message: { content: "fallback內容" } }] }),
      { status: 200, headers: { "content-type": "application/json" } }));
    const out = await kimiChat({ model: "kimi-k2.6", prompt: "test" });
    expect(out).toBe("fallback內容");
    expect(m).toHaveBeenCalledTimes(2);
    const secondBody = JSON.parse(String(m.mock.calls[1][1]?.body));
    expect(secondBody.stream).toBeUndefined();
  });
});

describe("manualViewJob watchdog 終態保證", () => {
  it("runner 掛起 + MANUAL_VIEW_JOB_TIMEOUT_MS=80 → job 被強制 failed（唔會永遠 running）", async () => {
    process.env.MANUAL_VIEW_JOB_TIMEOUT_MS = "80";
    _setManualViewRunnerForTest(() => new Promise(() => {})); // 永不 settle 嘅 hang job
    const r = submitManualView({ expertName: "測試專家", title: "測試標題", content: "字幕級證據內容。".repeat(20) });
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(getManualViewJob(r.jobId).status).toBe("running");
    await new Promise(res => setTimeout(res, 250));
    const j = getManualViewJob(r.jobId);
    expect(j.status).toBe("failed");
    expect(j.error).toMatch(/結構化超時/);
  });
});

describe("netCheck kome 探針誠實化", () => {
  it("kome /api/transcript 回 429 → kome=false 且 komeDetail 提及 429/付費", async () => {
    vi.mocked(fetch).mockImplementation(async (input: any) => {
      const url = String(input?.url ?? input);
      if (url.includes("kome.ai/api/transcript")) return new Response("Too Many Requests", { status: 429 });
      throw new TypeError("fetch failed"); // 其他探針（googleapis/youtube/brave/agent-gw）全部不可達
    });
    const r = await netCheck();
    expect(r.kome).toBe(false);
    expect(r.komeDetail).toMatch(/429|付費/);
  });

  it("kome 回 checkpoint HTML（即使 200）→ kome=false 且 detail 係安全閘道封鎖", async () => {
    vi.mocked(fetch).mockImplementation(async (input: any) => {
      const url = String(input?.url ?? input);
      if (url.includes("kome.ai/api/transcript")) {
        return new Response("<html><body>Vercel Security Checkpoint</body></html>", { status: 200, headers: { "content-type": "text/html" } });
      }
      throw new TypeError("fetch failed");
    });
    const r = await netCheck();
    expect(r.kome).toBe(false);
    expect(r.komeDetail).toMatch(/安全閘道封鎖/);
  });

  it("kome 回真實 JSON transcript → kome=true「可用」", async () => {
    vi.mocked(fetch).mockImplementation(async (input: any) => {
      const url = String(input?.url ?? input);
      if (url.includes("kome.ai/api/transcript")) {
        return new Response(JSON.stringify({ transcript: "字幕內容".repeat(100) }), { status: 200, headers: { "content-type": "application/json" } });
      }
      throw new TypeError("fetch failed");
    });
    const r = await netCheck();
    expect(r.kome).toBe(true);
    expect(r.komeDetail).toBe("可用");
  });
});
