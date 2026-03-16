#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


COOKIE_BUTTON_TEXTS = [
    "Accept",
    "Accept all",
    "I agree",
    "Agree",
    "Got it",
    "Continue",
    "OK",
    "Allow all",
]


def dismiss_common_overlays(page) -> None:
    for text in COOKIE_BUTTON_TEXTS:
        try:
            locator = page.get_by_role("button", name=text, exact=False).first
            if locator.count():
                locator.click(timeout=1200)
                page.wait_for_timeout(500)
        except Exception:
            pass


def nudge_lazy_content(page) -> None:
    try:
        page.evaluate(
            """
            () => {
              const h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
              window.scrollTo(0, Math.min(600, Math.floor(h * 0.12)));
            }
            """
        )
        page.wait_for_timeout(350)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(350)
    except Exception:
        pass


def wait_page_ready(page, wait_ms: int, ready_selector: str | None, ready_text: str | None) -> None:
    page.wait_for_load_state("domcontentloaded", timeout=120000)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    try:
        page.evaluate("""() => document.fonts ? document.fonts.ready : Promise.resolve()""")
    except Exception:
        pass
    dismiss_common_overlays(page)
    nudge_lazy_content(page)
    if ready_selector:
        page.locator(ready_selector).first.wait_for(state="visible", timeout=20000)
    if ready_text:
        page.get_by_text(ready_text, exact=False).first.wait_for(state="visible", timeout=20000)
    page.wait_for_timeout(wait_ms)


def target_locator(page, selector: str | None, text: str | None):
    if selector:
        locator = page.locator(selector).first
        if locator.count():
            return locator
    if text:
        locator = page.get_by_text(text, exact=False).first
        if locator.count():
            return locator
    return None


def add_highlight(page, locator, label: str | None = None, style: str = "smart", show_dot: bool = False) -> None:
    page.evaluate(
        """
        ({ element, label, style, showDot }) => {
          for (const id of ['__md_evidence_highlight__', '__md_evidence_cursor__', '__md_evidence_label__']) {
            const old = document.getElementById(id);
            if (old) old.remove();
          }

          const rect = element.getBoundingClientRect();
          const shortBlock = rect.height <= 90;
          const mode = style === 'smart' ? (shortBlock ? 'marker' : 'underline') : style;

          const overlay = document.createElement('div');
          overlay.id = '__md_evidence_highlight__';
          overlay.style.position = 'fixed';
          overlay.style.left = `${Math.max(8, rect.left - 8)}px`;
          overlay.style.width = `${Math.min(window.innerWidth - Math.max(8, rect.left - 8) - 12, rect.width + 16)}px`;
          overlay.style.zIndex = '2147483646';
          overlay.style.pointerEvents = 'none';
          overlay.style.borderRadius = '10px';

          if (mode === 'box') {
            overlay.style.top = `${Math.max(8, rect.top - 6)}px`;
            overlay.style.height = `${rect.height + 12}px`;
            overlay.style.border = '2px solid rgba(255, 77, 79, 0.9)';
            overlay.style.background = 'rgba(255, 235, 59, 0.08)';
          } else if (mode === 'underline') {
            overlay.style.top = `${Math.max(8, rect.top + rect.height - 5)}px`;
            overlay.style.height = '5px';
            overlay.style.background = 'rgba(255, 214, 10, 0.5)';
            overlay.style.borderBottom = '2px solid rgba(255, 77, 79, 0.9)';
            overlay.style.borderRadius = '6px';
          } else {
            overlay.style.top = `${Math.max(8, rect.top - 2)}px`;
            overlay.style.height = `${rect.height + 4}px`;
            overlay.style.background = 'rgba(255, 241, 118, 0.22)';
            overlay.style.border = '1px solid rgba(255, 77, 79, 0.45)';
          }
          document.body.appendChild(overlay);

          if (showDot) {
            const cursor = document.createElement('div');
            cursor.id = '__md_evidence_cursor__';
            cursor.style.position = 'fixed';
            cursor.style.left = `${Math.max(12, rect.left + 12)}px`;
            cursor.style.top = `${Math.max(12, rect.top + Math.min(16, rect.height * 0.28))}px`;
            cursor.style.width = '14px';
            cursor.style.height = '14px';
            cursor.style.borderRadius = '50%';
            cursor.style.background = '#ff4d4f';
            cursor.style.border = '2px solid white';
            cursor.style.boxShadow = '0 3px 8px rgba(0,0,0,0.18)';
            cursor.style.zIndex = '2147483647';
            cursor.style.pointerEvents = 'none';
            document.body.appendChild(cursor);
          }

          if (label) {
            const tag = document.createElement('div');
            tag.id = '__md_evidence_label__';
            tag.textContent = label;
            tag.style.position = 'fixed';
            tag.style.left = `${Math.max(12, rect.left)}px`;
            tag.style.top = `${Math.max(12, rect.top - 40)}px`;
            tag.style.maxWidth = '68vw';
            tag.style.padding = '8px 12px';
            tag.style.background = '#0f172a';
            tag.style.color = 'white';
            tag.style.fontSize = '15px';
            tag.style.fontWeight = '700';
            tag.style.lineHeight = '1.25';
            tag.style.borderRadius = '10px';
            tag.style.boxShadow = '0 8px 20px rgba(0,0,0,0.22)';
            tag.style.zIndex = '2147483647';
            tag.style.pointerEvents = 'none';
            document.body.appendChild(tag);
          }
        }
        """,
        {"element": locator.element_handle(), "label": label, "style": style, "showDot": show_dot},
    )


def adjust_clip_to_aspect(box: dict, viewport: dict, pad: int, min_aspect: float, max_aspect: float) -> dict:
    x = max(0, box["x"] - pad)
    y = max(0, box["y"] - int(pad * 1.1))
    width = min(viewport["width"] - x, box["width"] + pad * 2)
    height = min(viewport["height"] - y, box["height"] + int(pad * 1.8) + 30)

    aspect = width / max(height, 1)

    if aspect > max_aspect:
        target_height = min(viewport["height"] - y, int(width / max_aspect))
        extra = max(0, target_height - height)
        grow_up = min(y, extra // 2)
        y -= grow_up
        remaining = extra - grow_up
        height = min(viewport["height"] - y, height + grow_up + remaining)
        aspect = width / max(height, 1)

    if aspect < min_aspect:
        target_width = min(viewport["width"] - x, int(height * min_aspect))
        extra = max(0, target_width - width)
        grow_left = min(x, extra // 2)
        x -= grow_left
        remaining = extra - grow_left
        width = min(viewport["width"] - x, width + grow_left + remaining)

    return {
        "x": max(0, x),
        "y": max(0, y),
        "width": max(1, width),
        "height": max(1, height),
    }


def capture(page, output: Path, locator, full_page: bool, pad: int, min_aspect: float, max_aspect: float) -> None:
    if locator is None:
        page.screenshot(path=str(output), full_page=full_page)
        return

    locator.scroll_into_view_if_needed(timeout=10000)
    page.wait_for_timeout(1200)
    box = locator.bounding_box()
    if not box:
        page.screenshot(path=str(output), full_page=full_page)
        return

    viewport = page.viewport_size or {"width": 1600, "height": 1200}
    clip = adjust_clip_to_aspect(box, viewport, pad, min_aspect, max_aspect)
    if clip["width"] < 100 or clip["height"] < 100:
        page.screenshot(path=str(output), full_page=full_page)
        return
    page.screenshot(path=str(output), clip=clip)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a HD screenshot with load verification and subtle visible highlight.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--wait-ms", type=int, default=2500)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--scale", type=float, default=2)
    parser.add_argument("--selector")
    parser.add_argument("--text")
    parser.add_argument("--ready-selector")
    parser.add_argument("--ready-text")
    parser.add_argument("--highlight-selector")
    parser.add_argument("--highlight-text")
    parser.add_argument("--highlight-label")
    parser.add_argument("--highlight-style", choices=["smart", "marker", "underline", "box"], default="smart")
    parser.add_argument("--show-dot", action="store_true")
    parser.add_argument("--no-highlight", action="store_true")
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--pad", type=int, default=40)
    parser.add_argument("--min-aspect", type=float, default=1.0, help="Minimum width/height ratio. Default 1.0 = 16:16 max tallness")
    parser.add_argument("--max-aspect", type=float, default=16/9, help="Maximum width/height ratio. Default 16:9")
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=120000)
            wait_page_ready(page, args.wait_ms, args.ready_selector or args.selector, args.ready_text or args.text)
            locator = target_locator(page, args.selector, args.text)
            highlight_locator = target_locator(page, args.highlight_selector or args.selector, args.highlight_text or args.text)
            if highlight_locator is not None:
                highlight_locator.scroll_into_view_if_needed(timeout=10000)
                page.wait_for_timeout(1200)
                if not args.no_highlight:
                    add_highlight(page, highlight_locator, args.highlight_label, args.highlight_style, args.show_dot)
                    page.wait_for_timeout(500)
                locator = highlight_locator
            capture(page, output, locator, args.full_page, args.pad, args.min_aspect, args.max_aspect)
        except PlaywrightTimeoutError as e:
            raise SystemExit(f"Timeout while capturing screenshot: {e}")
        finally:
            try:
                browser.close()
            except Exception:
                pass
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
