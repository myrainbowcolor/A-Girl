"""用无头浏览器确定性验证数字人口型同步：
打开页面 → 发送消息 → 高频采样嘴部 SVG 路径的"上下唇间距" → 统计开合次数。

运行：python scripts/verify_lipsync.py   （需先启动 8011 服务）
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8011/"
_NUM = re.compile(r"-?\d+\.?\d*")


def mouth_gap(d: str) -> float:
    """解析 mouth 路径，返回 下唇中点Y - 上唇中点Y（越大=张口越大）。"""
    if not d:
        return 0.0
    nums = [float(x) for x in _NUM.findall(d)]
    # 路径: M (x cornerY) Q (cx upperMidY) (x2 cornerY) Q (cx lowerMidY) (x cornerY) Z
    # 索引: 0,1        2,3              4,5          6,7            8,9
    if len(nums) < 8:
        return 0.0
    upper_mid_y, lower_mid_y = nums[3], nums[7]
    return round(lower_mid_y - upper_mid_y, 2)


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_selector("#mouth")
        page.fill("#input", "今天发生了好多事情我想跟你慢慢说说你要好好听我讲完哦")
        page.click("#send")

        samples = []
        t0 = time.time()
        while time.time() - t0 < 4.0:
            d = page.get_attribute("#mouth", "d") or ""
            samples.append(mouth_gap(d))
            time.sleep(0.04)
        browser.close()

    gaps = samples
    mx, mn = max(gaps), min(gaps)
    # 统计跨越中线阈值的"张口"事件次数
    thr = (mx + mn) / 2 if mx > 1 else 5
    opens = 0
    above = False
    for g in gaps:
        if g > thr and not above:
            opens += 1
            above = True
        elif g <= thr:
            above = False

    print(f"采样点数={len(gaps)}  最大张口间距={mx}  最小={mn}")
    print(f"判定阈值={thr:.1f}  检测到张口次数={opens}")
    ok = mx >= 20 and opens >= 3
    print("结果:", "✅ 口型反复开合，同步生效" if ok else "❌ 未检测到明显反复开合")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
