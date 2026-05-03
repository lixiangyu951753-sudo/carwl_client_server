---
name: "drissionpage"
description: "DrissionPage v4.x 浏览器自动化开发助手。Invoke when writing or debugging code using DrissionPage (ChromiumPage, Chromium, ChromiumOptions), including browser control, element location, download, shadow DOM, and anti-detection."
---

# DrissionPage v4.1.x 开发技能

> 版本：4.1.1.2 | Python 3.6+ | Chromium 内核浏览器

## 一、核心对象

### 1.1 ChromiumPage — 标签页控制器

最常用的入口。可以接管已有浏览器标签页，也可以启动新浏览器。

```python
from DrissionPage import ChromiumPage, ChromiumOptions

# 方式1：自动寻找可用浏览器或启动新浏览器
page = ChromiumPage()

# 方式2：启动新浏览器（推荐，避免端口冲突）
co = ChromiumOptions().auto_port()
page = ChromiumPage(co)

# 方式3：连接已有浏览器（调试用）
co = ChromiumOptions()
co.set_local_port(9222)
page = ChromiumPage(addr_or_opts=co)
```

**关键区别**：
- `ChromiumPage()` 无参 → 先尝试查找已有浏览器，找不到就启动新的
- `auto_port()` → 总是启动新浏览器，自动选择可用端口
- `set_local_port(N)` → 连接指定端口的已有浏览器（用于调试已打开的浏览器）

### 1.2 Chromium — 浏览器管理器

管理整个浏览器进程，可以创建多个标签页。

```python
from DrissionPage import Chromium, ChromiumOptions

# 启动或连接浏览器
co = ChromiumOptions().auto_port()
browser = Chromium(co)

tab = browser.latest_tab      # 获取最新标签页
new_tab = browser.new_tab()   # 创建新标签页
browser.quit()                # 关闭浏览器
```

### 1.3 ChromiumOptions — 浏览器配置

```python
co = ChromiumOptions()
co.auto_port()                           # 自动端口（推荐）
co.set_local_port(9222)                  # 固定端口
co.set_argument('--no-first-run')        # 禁用首次运行向导
co.set_argument('--no-default-browser-check')
co.set_argument('--disable-blink-features=AutomationControlled')  # 反检测
co.headless(True)                        # 无头模式
co.set_user_data_path('./user_data')     # 用户数据目录（保存登录态）
co.set_paths(browser_path=r'C:\...chrome.exe')  # 指定浏览器路径
```

## 二、元素定位

### 2.1 定位语法（LOCATOR）

| 语法 | 说明 | 示例 |
|------|------|------|
| `'@id'` 或 `'#id'` | id 属性 | `'#main'` |
| `'@class'` 或 `'.class'` | class 属性 | `'.price'` |
| `'tag:div'` | 标签名 | `'tag:input'` |
| `'@name=xxx'` | 任意属性 | `'@data-id=123'` |
| `'text=xxx'` | 文本内容 | `'text=下一页'` |
| `'@text()=xxx'` | 包含文本 | `'@text()=商品'` |
| `'css:selector'` | CSS 选择器 | `'css:.container>div'` |
| `'x://...'` | XPath（以 x: 开头） | `'x://div[@class="price"]'` |
| `'xpath://...'` | XPath（以 xpath: 开头） | `'xpath://span/text()'` |

**链式查找**：
```python
# 先找父元素，再在父元素下找子元素
parent = page.ele('.container')
child = parent.ele('tag:span')
children = parent.eles('tag:div')
```

### 2.2 核心方法

```python
# 查找单个元素，默认 timeout=10秒
elem = page.ele('#main', timeout=5)
elem = page.ele('x://div[@class="price"]')
elem = page.ele('.ant-checkbox-input')

# 查找多个元素
divs = page.eles('tag:div')
items = page.eles('.list-item')

# 超时处理：查不到返回 None 而非抛异常
elem = page.ele('#not-exist', timeout=1)
print(elem)  # None

# 等待元素出现
from DrissionPage.common import wait_until
elem = page.wait.ele_displayed('#content', timeout=10)
```

## 三、元素操作

### 3.1 基础操作

```python
elem.click()                    # 点击
elem.click(by_js=True)         # 通过 JS 点击（绕过遮罩）
elem.input('hello')            # 输入文本
elem.clear()                   # 清空输入框
elem.attr('src')               # 获取属性
elem.attr('href')
elem.text                      # 获取文本
elem.html                      # 获取 innerHTML
elem.link                      # 获取 href（a 标签）
```

### 3.2 模拟操作 / 拖拽

```python
# 创建动作链
act = page.actions

# 滑块验证码拖拽示例
slder = page.ele('#nc_1_n1z')
distance = 280  # 滑块距离
track = generate_human_track(distance)  # 生成人类轨迹

act.hold(slder)
for dx, dy, dt in track:
    act.move(dx, dy)
    time.sleep(dt)
act.release()
```

### 3.3 运行 JavaScript

```python
# 执行 JS 并获取返回值
result = page.run_js('return document.title')

# 操作 Shadow DOM 内的元素
page.run_js("""
    const toolbar = document.getElementById('market-mate-offer-list-toolbar');
    if (toolbar && toolbar.shadowRoot) {
        const checkbox = toolbar.shadowRoot.querySelector('.ant-checkbox-input');
        if (checkbox) checkbox.click();
    }
""")
```

## 四、页面操作

### 4.1 导航和标签页管理

```python
# 导航
page.get('https://www.1688.com')
page.latest_tab.wait(3)        # 等待加载

# 标签页管理
tab = page.latest_tab          # 获取最新标签页
tab.close()                    # 关闭当前标签页
new_tab = page.new_tab('https://...')  # 新建标签页并导航
new_tab.close()                # 关闭新建的标签页

# 查看所有标签页
for tab in page.get_tabs():
    print(tab.title)

# 切换到指定标签页
tab = page.get_tab(1)          # 切换到第2个标签页
```

### 4.2 等待

```python
page.wait(3)                   # 等待3秒
page.wait.ele_deleted('.loading', timeout=10)  # 等待元素消失
page.wait.doc_loaded()         # 等待文档加载完成
```

### 4.3 滚动

```python
page.scroll.to_bottom()        # 滚动到底部
page.scroll.to_top()           # 滚动到顶部
page.scroll.to_location(0, 500)  # 滚动到指定位置
page.scroll.to_see('#footer')  # 滚动到元素可见

# 模拟人类滚动（多次）
for i in range(5):
    page.scroll.to_bottom()
    page.wait(1)
```

### 4.4 截图和保存

```python
page.save(path='./output')           # 保存 MHTML
page.get_screenshot('screenshot.png') # 截取整个网页
```

## 五、下载功能

```python
# 推荐方式：使用浏览器内置下载（支持大文件、验证cookie）
page.download(url, save_path)

# 带重命名的下载
page.download(url, save_path, rename='new_name.jpg')

# 批量下载图片
for img_url in image_urls:
    page.download(img_url, './images')
```

**注意事项**：
- 下载方法自动处理 Cookie 和 Referer
- 下载路径必须存在，否则报错
- 不支持断点续传

## 六、Shadow DOM 处理

```python
# 获取元素的 Shadow Root
shadow = page.ele('.html-description').shadow_root

# 在 Shadow DOM 内定位
imgs = shadow.eles('x://*[@id="detail"]/p[2]/span/strong/img')
for img in imgs:
    src = img.attr('src')
```

**注意**：只有 `open` 模式的 Shadow DOM 可通过 `shadow_root` 访问。`closed` 模式需要用 `run_js()`。

## 七、浏览器生命周期管理（本项目最佳实践）

### 7.1 健康检查 + 自动重建

```python
browser = None

def init_browser():
    global browser
    co = ChromiumOptions()
    co.auto_port()              # 自动端口避免冲突
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')
    browser = ChromiumPage(co)
    return browser

def get_browser():
    global browser
    if browser is None:
        return init_browser()
    try:
        _ = browser.latest_tab   # 快速健康检查
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

### 7.2 使用模式

```python
def crawl_callback(task_id, params):
    shop_url = params.get('shop_url')
    if shop_url:
        get_browser().get(shop_url)
        get_browser().latest_tab.wait(3)

def shop_detail():
    b = get_browser()           # 函数开头获取一次
    tab = b.latest_tab
    # ... 大量操作 ...
    b.download(img_url, path)

def shop_list():
    while retry_count < max_retry:
        try:
            tab = get_browser().latest_tab  # 每次循环重新获取
            # ...
        except Exception:
            # 重试时 get_browser() 会自动重建
            get_browser().get(shop_url)
```

### 7.3 断连场景处理

| 场景 | 原因 | 处理方式 |
|------|------|----------|
| `auto_port()` 无参 | 浏览器从未启动 | `get_browser()` 首次调用时自动 `init_browser()` |
| `set_local_port(9222)` | 连接已有浏览器 | 仅适用于已打开的浏览器调试 |
| 浏览器崩溃/关闭 | 外部关闭了浏览器进程 | `get_browser()` 检测到断连后自动重建 |
| 网络断开 | CDP 连接超时 | 异常捕获后重试，下次 `get_browser()` 触发重建 |

## 八、常见错误与解决

### 8.1 "与页面的连接已断开"

**原因**：浏览器进程已关闭/崩溃，或 CDP 连接超时。

**解决**：
1. 检查浏览器是否还在运行
2. 使用 `auto_port()` 而非 `set_local_port()` 启动新浏览器
3. 添加 `get_browser()` 健康检查 + 自动重建

### 8.2 "与浏览器连接失败"

**原因**：`set_local_port(9222)` 但该端口没有浏览器在监听。

**解决**：改用 `auto_port()` 自动启动浏览器。

### 8.3 元素找不到返回 None

**原因**：元素未加载完成或页面结构变化。

**解决**：
```python
# 增加等待
page.wait(3)
# 增加超时时间
elem = page.ele('.target', timeout=10)
# 如果还是 None，说明选择器过期
elem = page.ele('.new-selector')
```

### 8.4 下载失败

**原因**：下载路径不存在。

**解决**：下载前确保目录存在：
```python
import os
if not os.path.exists(save_path):
    os.makedirs(save_path)
page.download(url, save_path)
```

## 九、反检测配置

```python
co = ChromiumOptions()
co.set_argument('--disable-blink-features=AutomationControlled')
co.set_argument('--disable-features=ChromeWhatsNewUI')
co.set_argument('--disable-gpu')
co.set_argument('--no-first-run')
# 有头模式（不要 headless，易被检测）
page = ChromiumPage(co)

# 修改 navigator.webdriver
page.run_js('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
```

## 十、项目中的典型用法

### 店铺列表页爬取（client/main.py）

```python
def shop_list(server_task_id=None, shop_url=None):
    while retry_count < max_retry:
        try:
            tab = get_browser().latest_tab     # 每次重试重新获取
            page_num = 1
            while True:
                # 分类选中检查
                cats = tab.eles('x://div[@class="first-category"]')
                # 商品列表
                divs = tab.eles('x://...')
                for div in divs:
                    if check_task_canceled():   # 停止检测
                        return {"status": "canceled", ...}
                    div.click()
                    tab.wait(1)
                    result = shop_detail(batch_id, server_task_id)
                # 翻页
                next_btn = tab.ele('下一页')
                next_btn.click()
                tab.wait(3)
        except Exception:
            retry_count += 1
            get_browser().get(shop_url)         # 自动重建+导航
```

### 插件导出 Excel（client2/main.py）

```python
def shop_list(server_task_id=None, shop_url=None):
    co = ChromiumOptions()
    co.auto_port()                              # 每次新建浏览器
    co.set_argument('--no-first-run')
    browser = Chromium(co)

    export_1688_products(browser, shop_url)     # 使用插件
    file = get_latest_1688_file()
    data = extract_product_data(file)
```

## 十一、与 Selenium 对比

| 特性 | DrissionPage | Selenium |
|------|-------------|----------|
| WebDriver | 不需要 | 需要下载对应版本 |
| 速度 | 快 | 较慢 |
| iframe 处理 | 直接跨 iframe 定位 | 需要 switch_to |
| 多标签页 | 同时操作 | 需要切换 |
| 下载 | 内置下载 | 需要额外配置 |
| Shadow DOM | 内置支持 | 需要用 JS |
| 学习曲线 | 语法简洁 | 概念较多 |

## 十二、版本注意

- **4.0+**：大版本重构，API 变化大，不兼容 3.x
- **auto_port()**：4.x 新增，自动分配端口
- **run_cdp()**：4.x 新增，直接发送 CDP 命令
- **ChromiumPage 与 Chromium**：4.x 中 ChromiumPage 接管一个标签页，Chromium 管理整个浏览器

## 十三、参考资料

- 官网：https://www.drissionpage.cn/
- GitHub：https://github.com/g1879/DrissionPage
- Gitee：https://gitee.com/g1879/DrissionPage
- 离线文档下载：https://www.drissionpage.cn/（有离线文档链接）
