---
name: drissionpage
description: DrissionPage v4.x 浏览器自动化开发助手。编写或调试 DrissionPage 代码时使用，包括 ChromiumPage、Chromium、ChromiumOptions、元素定位、下载、Shadow DOM、反检测等。
---

# DrissionPage v4.1.x 开发技能

> 版本：4.1.1.2 | Python 3.6+ | Chromium 内核浏览器

## 一、核心对象

### ChromiumPage — 标签页控制器

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# 推荐：启动新浏览器，避免端口冲突
co = ChromiumOptions().auto_port()
page = ChromiumPage(co)

# 无参：先尝试查找已有浏览器，找不到就启动新的
page = ChromiumPage()

# 连接已有浏览器（调试用）
co = ChromiumOptions()
co.set_local_port(9222)
page = ChromiumPage(addr_or_opts=co)
```

### Chromium — 浏览器管理器

```python
from DrissionPage import Chromium, ChromiumOptions

co = ChromiumOptions().auto_port()
browser = Chromium(co)
tab = browser.latest_tab
new_tab = browser.new_tab()
browser.quit()
```

### ChromiumOptions — 浏览器配置

```python
co = ChromiumOptions()
co.auto_port()
co.set_argument('--no-first-run')
co.set_argument('--no-default-browser-check')
co.set_argument('--disable-blink-features=AutomationControlled')
co.headless(True)
co.set_user_data_path('./user_data')
co.set_paths(browser_path=r'C:\...chrome.exe')
```

## 二、元素定位

| 语法 | 说明 | 示例 |
|------|------|------|
| `'@id'` 或 `'#id'` | id 属性 | `'#main'` |
| `'@class'` 或 `'.class'` | class 属性 | `'.price'` |
| `'tag:div'` | 标签名 | `'tag:input'` |
| `'@name=xxx'` | 任意属性 | `'@data-id=123'` |
| `'text=xxx'` | 文本内容 | `'text=下一页'` |
| `'css:selector'` | CSS 选择器 | `'css:.container>div'` |
| `'x://...'` | XPath | `'x://div[@class="price"]'` |

```python
# 链式查找
parent = page.ele('.container')
child = parent.ele('tag:span')
children = parent.eles('tag:div')

# 超时处理：查不到返回 None
elem = page.ele('#not-exist', timeout=1)  # None
```

## 三、元素操作

```python
elem.click()
elem.click(by_js=True)      # JS 点击绕过遮罩
elem.input('hello')
elem.clear()
elem.attr('src')            # 获取属性
elem.text                   # 获取文本
elem.html                   # innerHTML
elem.link                   # href（a 标签）

# JS 执行
result = page.run_js('return document.title')
```

## 四、滑块验证与动作链

```python
act = page.actions
slder = page.ele('#nc_1_n1z')
act.hold(slder)
for dx, dy, dt in track:
    act.move(dx, dy)
    time.sleep(dt)
act.release()
```

## 五、Shadow DOM

```python
# open 模式的 Shadow DOM
shadow = page.ele('.element').shadow_root
imgs = shadow.eles('x://img')

# closed 模式用 JS
page.run_js('document.querySelector("elem").shadowRoot.querySelector("input").click()')
```

## 六、页面操作

```python
page.get('https://www.1688.com')
tab = page.latest_tab
tab.close()
new_tab = page.new_tab('https://...')

page.wait(3)
page.wait.ele_deleted('.loading', timeout=10)
page.scroll.to_bottom()
page.get_screenshot('screenshot.png')
```

## 七、下载

```python
page.download(url, save_path)
page.download(url, save_path, rename='new_name.jpg')
# 下载前确保目录存在
import os
if not os.path.exists(save_path):
    os.makedirs(save_path)
```

## 八、浏览器生命周期管理（最佳实践）

```python
browser = None

def init_browser():
    global browser
    co = ChromiumOptions()
    co.auto_port()
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')
    browser = ChromiumPage(co)
    return browser

def get_browser():
    global browser
    if browser is None:
        return init_browser()
    try:
        _ = browser.latest_tab   # 健康检查
        return browser
    except Exception:
        print("浏览器断开，重新创建...")
        try:
            browser.quit()
        except Exception:
            pass
        browser = None
        return init_browser()
```

## 九、反检测

```python
co = ChromiumOptions()
co.set_argument('--disable-blink-features=AutomationControlled')
co.set_argument('--disable-features=ChromeWhatsNewUI')
co.set_argument('--disable-gpu')
co.set_argument('--no-first-run')
# 不要用 headless，易被检测
page = ChromiumPage(co)
page.run_js('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
```

## 十、常见错误

- **"与页面的连接已断开"**: 浏览器崩溃或网络断开 → 使用 `auto_port()` + `get_browser()` 自动重建
- **"与浏览器连接失败"**: `set_local_port` 但端口无监听 → 改用 `auto_port()`
- **元素返回 None**: 未加载完成 → 增加 `timeout` 或 `page.wait(3)`
- **下载失败**: 路径不存在 → 下载前 `os.makedirs()`
