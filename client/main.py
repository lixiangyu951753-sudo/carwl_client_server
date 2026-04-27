import os
import re
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse

import requests
from DrissionPage import ChromiumPage

from api_client import ClientAPI
from task_manager import TaskManager
import config

browser = ChromiumPage()
base_path = config.BASE_PATH
tasks_file = os.path.join(base_path, 'tasks.json')
batch_file = os.path.join(base_path, 'batch.json')

api = ClientAPI(config.CLIENT_ID, config.SERVER_URL)
manager = TaskManager(api, config.HEARTBEAT_INTERVAL)

def gen_batch_id() -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S')

def load_batch() -> dict:
    if os.path.exists(batch_file):
        with open(batch_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_batch(batch_id: str, status: str, product_count: int = 0):
    batches = load_batch()
    batches[batch_id] = {
        'status': status,
        'product_count': product_count,
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)

def gen_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return hashlib.md5(base_url.encode('utf-8')).hexdigest()[:16]

def load_tasks() -> dict:
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_task(task_id: str, status: str, file_name: str = None, url: str = None, batch_id: str = None, error: str = None):
    tasks = load_tasks()
    tasks[task_id] = {
        'status': status,
        'file_name': file_name,
        'url': url,
        'batch_id': batch_id,
        'error': error,
        'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def is_task_completed(task_id: str) -> bool:
    tasks = load_tasks()
    if task_id in tasks:
        return tasks[task_id].get('status') == 'completed'
    return False

def shop_detail(batch_id: str, server_task_id: str = None):
    tab_detail = browser.latest_tab
    product_url = tab_detail.url
    task_id = gen_id_from_url(product_url)
    print(f"任务ID: {task_id}")

    if is_task_completed(task_id):
        print(f"任务已跳过（之前已爬取）: {tab_detail.title}")
        tab_detail.close()
        return None

    save_task(task_id, 'running', file_name=tab_detail.title, url=product_url, batch_id=batch_id)

    if server_task_id:
        api.report_progress(server_task_id, "running", progress={
            "current_product": task_id,
            "status": "crawling"
        })

    file_name = tab_detail.title
    file_name = os.path.join(base_path, file_name)
    print(file_name)
    if not os.path.exists(file_name):
        os.makedirs(file_name)
        print(file_name + '文件夹已创建')
    else:
        print(file_name + '文件夹已存在')

    divs = tab_detail.ele(".od-scroller-list").eles("tag:div")
    print(len(divs))
    for div in divs:
        style = div.ele('tag:span').attr('style')
        print(style)
        pattern = r'url\("([^"]+)"'
        match = re.search(pattern, style)
        if match:
            img_url = match.group(1)
            img_url = img_url.replace("_b.jpg", "_.webp")
            print(img_url)
            if os.path.exists(os.path.join(file_name, os.path.basename(img_url))):
                print('图片已存在，跳过下载')
            else:
                print(img_url + '不存在，开始下载')
                browser.download(img_url, file_name)
        else:
            print('未找到图片URL')

    shadow_root = tab_detail.ele('.html-description').shadow_root
    print("======================================", shadow_root)
    imgs_list = shadow_root.eles('x://*[@id="detail"]/p[2]/span/strong/img')
    print(len(imgs_list))
    factory_dir = os.path.join(file_name, 'factory')
    if not os.path.exists(factory_dir):
        os.makedirs(factory_dir)
        print(factory_dir + '文件夹已创建')
    else:
        print(factory_dir + '文件夹已存在')
    for index, img in enumerate(imgs_list):
        if index == 0:
            continue
        img_url = img.attr('src')
        print(img_url)
        img_name = os.path.basename(img_url)

        if index < len(imgs_list) - 3:
            if os.path.exists(os.path.join(file_name, img_name)):
                print('图片已存在，跳过下载')
            else:
                browser.download(img_url, file_name)
        else:
            if os.path.exists(os.path.join(factory_dir, img_name)):
                print('图片已存在，跳过下载')
            else:
                browser.download(img_url, factory_dir)

    try:
        lib_video = tab_detail.ele(".lib-video", timeout=3).ele("tag:video", timeout=3)
    except:
        lib_video = None
        print('未找到视频')
        save_task(task_id, 'completed', file_name=file_name, url=product_url, batch_id=batch_id)
        return {
            "task_id": task_id,
            "title": tab_detail.title,
            "url": product_url,
            "status": "completed",
            "local_folder": file_name
        }

    if lib_video:
        video_url = lib_video.attr('src')
        print(video_url)
        video_tab = browser.new_tab(video_url)
        browser.download(video_tab.url, file_name)
        video_tab.close()
    else:
        print('未找到视频')

    for i in range(5):
        tab_detail.scroll.to_bottom()
        tab_detail.wait(1)

    tab_detail.save(path=file_name)
    
    # 在关闭标签页之前保存需要的信息
    task_title = tab_detail.title
    
    tab_detail.close()
    print('关闭当前详情标签页')
    save_task(task_id, 'completed', file_name=file_name, url=product_url, batch_id=batch_id)
    print("任务完成")
    save_task(task_id, 'completed', url=product_url, batch_id=batch_id)

    return {
        "task_id": task_id,
        "title": task_title,
        "url": product_url,
        "status": "completed",
        "local_folder": file_name
    }



def shop_list(server_task_id: str = None, shop_url: str = None):
    batch_id = gen_batch_id()
    print(f"开始新批次任务: {batch_id}, 店铺URL: {shop_url}")
    save_batch(batch_id, 'running')

    max_retry = 3
    retry_count = 0
    
    while retry_count < max_retry:
        try:
            tab = browser.latest_tab
            completed_count = 0
            page_num = 1
            products = []

            while True:
                print(f"\n===== 第 {page_num} 页 =====")
                #判断是否在目标页
                categorys = tab.eles('x://div[@class="first-category"]')
                
                if categorys:
                    first_cat_style = categorys[0].attr('style') or ''
                    is_selected = 'bold' in first_cat_style
                    print(f"第一个分类选中状态: {is_selected}")
                    
                    if not is_selected:
                        print("第一个分类未选中，点击第一个分类")
                        categorys[0].click()
                        tab.wait(1)

                #商品列表
                
                divs = tab.eles('x://*[@id="bd_1_container_0"]/div/div[2]/div[5]/div')
                if len(divs) == 0:
                    print('网页未安装插件，使用新的定位方式')
                    divs=tab.eles('x://*[@id="bd_1_container_0"]/div/div[2]/div[6]/div')

                print(f"本页商品数量: {len(divs)}")

                for div in divs:
                    print(div.text)
                    div.click()
                    tab.wait(1)
                    result = shop_detail(batch_id, server_task_id)
                    if result:
                        products.append(result)
                    completed_count += 1
                    tab.wait(3)

                    if server_task_id:
                        api.report_progress(server_task_id, "running", progress={
                            "current_page": page_num,
                            "current_product": completed_count
                        })

                next_btn = tab.ele('下一页')
                if not next_btn:
                    print("未找到下一页按钮，停止翻页")
                    break

                style = next_btn.attr('style') or ''
                if 'rgb(204, 204, 204)' in style:
                    print("下一页按钮不可用，停止翻页")
                    break

                print("点击下一页")
                next_btn.click()
                tab.wait(3)
                page_num += 1

            save_batch(batch_id, 'completed', product_count=completed_count)
            print(f"\n批次 {batch_id} 完成，共爬取 {completed_count} 个商品，总页数 {page_num} 页")

            return {
                "batch_id": batch_id,
                "products": products
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"[错误] 浏览器连接异常: {error_msg}")
            retry_count += 1
            
            if retry_count < max_retry:
                print(f"[重试] 第 {retry_count} 次重试，重新打开浏览器...")
                if server_task_id:
                    api.report_progress(server_task_id, "running", progress={
                        "status": "reconnecting",
                        "retry": retry_count
                    })
                
                # 重新打开浏览器并进入目标页
                if shop_url:
                    print(f"[爬虫] 重新打开店铺: {shop_url}")
                    browser.get(shop_url)
                    browser.latest_tab.wait(3)
                else:
                    print("[爬虫] 未提供店铺URL，无法重新打开")
                    if server_task_id:
                        api.report_progress(server_task_id, "failed", error="浏览器连接断开且未提供店铺URL")
                    return {
                        "batch_id": batch_id,
                        "products": [],
                        "error": "浏览器连接断开且未提供店铺URL"
                    }
            else:
                print(f"[错误] 重试 {max_retry} 次后仍然失败")
                if server_task_id:
                    api.report_progress(server_task_id, "failed", error=f"浏览器连接断开，重试{max_retry}次后失败: {error_msg}")
                return {
                    "batch_id": batch_id,
                    "products": [],
                    "error": f"浏览器连接断开，重试{max_retry}次后失败"
                }

def crawl_callback(task_id: str, params: dict):
    """任务管理器回调函数"""
    shop_url = params.get('shop_url')
    max_pages = params.get('max_pages')

    if shop_url:
        print(f"[爬虫] 打开店铺: {shop_url}")
        browser.get(shop_url)
        browser.latest_tab.wait(3)
    else:
        print(f"[爬虫] 未提供店铺URL，任务 {task_id} 使用浏览器默认打开的网页")
        browser.latest_tab.wait(1)

    result = shop_list(server_task_id=task_id, shop_url=shop_url)
    return result

def main():
    print("=" * 50)
    print("  1688远程控制爬虫客户端")
    print("=" * 50)

    manager.set_crawl_callback(crawl_callback)
    manager.run()

if __name__ == '__main__':
    main()
