import { describe, it, expect } from "vitest";
import { safeEq, expectedToken, cookieAuthed, loginThrottle, COOKIE_NAME, gateEnabled, envFromFile } from "./gate-core";

describe("gate-core", () => {
  it("safeEq 長度不同直接 false（不拋錯）", () => {
    expect(safeEq("abc", "abcd")).toBe(false);
    expect(safeEq("", "")).toBe(true);
  });

  it("expectedToken 是穩定的 64 位 hex", () => {
    const t = expectedToken();
    expect(t).toMatch(/^[0-9a-f]{64}$/);
    expect(expectedToken()).toBe(t); // 無狀態：同輸入同輸出
  });

  it("cookieAuthed 正確 token 通過、錯誤/畸形 token 拒絕", () => {
    if (!gateEnabled) return; // 門禁關閉時無可測
    expect(cookieAuthed(`${COOKIE_NAME}=${expectedToken()}`)).toBe(true);
    expect(cookieAuthed(`${COOKIE_NAME}=deadbeef`)).toBe(false);
    expect(cookieAuthed(`${COOKIE_NAME}=%E0%A4%A`)).toBe(false); // 畸形 % 序列不得拋錯
    expect(cookieAuthed(undefined)).toBe(false);
    expect(cookieAuthed("other=1")).toBe(false);
  });

  it("loginThrottle 每 IP 10 次後拒絕，且按 IP 隔離", () => {
    const ip = "test-203.0.113.1";
    for (let i = 0; i < 10; i++) expect(loginThrottle(ip)).toBe(true);
    expect(loginThrottle(ip)).toBe(false); // 第 11 次被拒
    expect(loginThrottle("test-203.0.113.2")).toBe(true); // 不同 IP 不受影響
  });

  it("envFromFile 能從 .env 讀到 ACCESS_CODE（dev 熱重載語義）", () => {
    expect(envFromFile("ACCESS_CODE").length).toBeGreaterThan(0);
  });
});
