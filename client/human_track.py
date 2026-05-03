import time
import random
import math


def ease_out_quint(t):
    return 1 - pow(1 - t, 5)


def generate_human_track(distance):
    """
    生成真人风格滑块轨迹
    返回格式:
    [(dx, dy, dt), ...]
    dx = 本次移动x
    dy = 本次移动y
    dt = 停顿秒数
    """

    track = []

    # 总耗时（真人常见 0.8~1.8 秒）
    total_time = random.uniform(0.9, 1.6)

    # 步数
    steps = random.randint(28, 42)

    # 过冲距离
    overshoot = random.randint(3, 8)

    target = distance + overshoot

    prev_x = 0

    for i in range(steps):
        t = (i + 1) / steps

        # 缓动曲线
        x = ease_out_quint(t) * target

        # 加一点随机扰动
        x += random.uniform(-1.2, 1.2)

        move = round(x - prev_x)

        if move == 0:
            continue

        prev_x += move

        # 微抖动
        dy = random.randint(-1, 1)

        # 随机间隔
        dt = total_time / steps + random.uniform(-0.01, 0.015)

        track.append((move, dy, dt))

    # 回拉修正
    back_steps = random.randint(2, 4)
    remain = prev_x - distance

    while remain > 0:
        step = min(random.randint(1, 3), remain)
        track.append((-step, random.randint(-1, 1), random.uniform(0.02, 0.05)))
        remain -= step

    # 最后微调
    final_fix = distance - sum(x[0] for x in track)
    if final_fix != 0:
        track.append((final_fix, 0, random.uniform(0.02, 0.04)))

    return track


if __name__ == '__main__':
    from DrissionPage import Chromium, ChromiumOptions

    options = ChromiumOptions()
    browser = Chromium(options)
    tab = browser.new_tab('https://detail.1688.com/offer/656742829692.html?_t=1777445697861&spm=a2615.7691456.co_0_0_wangpu_score_0_0_0_0_0_0_0000_0.0')

    slder = tab.ele('#nc_1_n1z')
    if slder:
        print('滑动条存在')
        distance = 280
        track = generate_human_track(distance)
        act = tab.actions
        act.hold(slder)
        for dx, dy, dt in track:
            act.move(dx, dy)
            time.sleep(dt)
        act.release()
        print("拖动完成")
