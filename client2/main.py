import os
import json
import glob
import re
from datetime import datetime

from DrissionPage import Chromium, ChromiumOptions
from api_client import ClientAPI
from task_manager import TaskManager
import config
from pathlib import Path


# 确保输出目录存在
if not os.path.exists(config.BASE_PATH):
    os.makedirs(config.BASE_PATH)

tasks_file = os.path.join(config.BASE_PATH, 'tasks.json')
batch_file = os.path.join(config.BASE_PATH, 'batch.json')

api = ClientAPI(config.CLIENT_ID, config.SERVER_URL, config.CLIENT_CAPABILITIES)
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


def get_latest_1688_file():
    """读取系统下载目录下商品列表-1688 开头最新的文件"""
    base_path = str(Path.home() / "Downloads")
    
    pattern = os.path.join(base_path, '商品列表-1688*.xlsx')
    files = glob.glob(pattern)
    
    if not files:
        print(f'[爬虫] 未找到匹配的文件：{pattern}')
        return None
    
    latest_file = max(files, key=os.path.getmtime)
    print(f'[爬虫] 找到最新文件：{latest_file}')
    return latest_file


def extract_product_data(file_path):
    """从 Excel 文件中提取商品数据"""
    import pandas as pd
    
    print(f'[爬虫] 读取文件：{file_path}')
    
    df = pd.read_excel(file_path)
    
    print(f'[爬虫] Excel 列名：{list(df.columns)}')
    
    data_list = []
    for index, row in df.iterrows():
        product_data = {
            'title': None,
            'productId': None,
            'price': None,
            'annualSalesCount': None,
            'annualSalesOrders': None,
            'repurchaseRate': None,
            'sourceUrl': None,
        }
        
        for col in df.columns:
            if '标题' in col:
                product_data['title'] = str(row[col]) if pd.notna(row[col]) else None
            elif '商品ID' in col:
                product_data['productId'] = str(row[col]) if pd.notna(row[col]) else None
            elif '价格' in col or '单价' in col:
                product_data['price'] = str(row[col]) if pd.notna(row[col]) else None
            elif '年销售' in col and '件' in col:
                product_data['annualSalesCount'] = str(row[col]) if pd.notna(row[col]) else None
            elif '年销售' in col and '笔' in col:
                product_data['annualSalesOrders'] = str(row[col]) if pd.notna(row[col]) else None
            elif '复购' in col:
                product_data['repurchaseRate'] = str(row[col]) if pd.notna(row[col]) else None
            elif '链接' in col or 'url' in col.lower():
                product_data['sourceUrl'] = str(row[col]) if pd.notna(row[col]) else None
        
        data_list.append(product_data)
    
    print(f'[爬虫] 共读取 {len(data_list)} 条商品数据')
    print(f'[爬虫] 前 3 条数据预览：')
    for item in data_list[:3]:
        print(f"  商品：{item.get('title', 'N/A')}")
        print(f"    商品ID：{item.get('productId', 'N/A')}")
        print(f"    价格：{item.get('price', 'N/A')}")
        print(f"    年销售件数：{item.get('annualSalesCount', 'N/A')}")
        print(f"    年销售笔数：{item.get('annualSalesOrders', 'N/A')}")
        print(f"    复购率：{item.get('repurchaseRate', 'N/A')}")
        print()
    
    return data_list


def export_1688_products(browser, shop_url: str):
    """使用 1688 插件导出商品列表 Excel"""
    tab = browser.latest_tab
    
    print(f"[爬虫] 打开店铺: {shop_url}")
    tab.get(shop_url)
    tab.wait(3)
    
    categorys = tab.eles('x://div[@class="first-category"]')
    
    if categorys:
        first_cat_style = categorys[0].attr('style') or ''
        is_selected = 'bold' in first_cat_style
        print(f"[爬虫] 第一个分类选中状态: {is_selected}")
        
        if not is_selected:
            print("[爬虫] 第一个分类未选中，点击第一个分类")
            categorys[0].click()
            tab.wait(1)
    
    # 检查全选复选框状态
    checkbox_checked = tab.run_js("""
        const toolbar = document.getElementById('market-mate-offer-list-toolbar');
        if (toolbar && toolbar.shadowRoot) {
            const toolbarContent = toolbar.shadowRoot.getElementById('1688-market-mate-toolbar');
            if (toolbarContent) {
                const checkbox = toolbarContent.querySelector('.ant-checkbox-input');
                if (checkbox) {
                    return checkbox.checked;
                }
            }
        }
        return false;
    """)
    
    print(f"[爬虫] 全选复选框状态：{'已选中' if checkbox_checked else '未选中'}")
    
    if not checkbox_checked:
        print("[爬虫] 复选框未选中，点击全选复选框...")
        tab.run_js("""
            const toolbar = document.getElementById('market-mate-offer-list-toolbar');
            if (toolbar && toolbar.shadowRoot) {
                const toolbarContent = toolbar.shadowRoot.getElementById('1688-market-mate-toolbar');
                if (toolbarContent) {
                    const checkboxLabel = toolbarContent.querySelector('.ant-checkbox-label');
                    if (checkboxLabel) {
                        checkboxLabel.click();
                    }
                }
            }
        """)
        tab.wait(1)
        
        checkbox_checked = tab.run_js("""
            const toolbar = document.getElementById('market-mate-offer-list-toolbar');
            if (toolbar && toolbar.shadowRoot) {
                const toolbarContent = toolbar.shadowRoot.getElementById('1688-market-mate-toolbar');
                if (toolbarContent) {
                    const checkbox = toolbarContent.querySelector('.ant-checkbox-input');
                    if (checkbox) {
                        return checkbox.checked;
                    }
                }
            }
            return false;
        """)
        print(f"[爬虫] 点击后复选框状态：{'已选中' if checkbox_checked else '未选中'}")
    
    # 点击导出表格按钮
    print("[爬虫] 点击导出表格按钮...")
    tab.run_js("""
        const toolbar = document.getElementById('market-mate-offer-list-toolbar');
        if (toolbar && toolbar.shadowRoot) {
            const toolbarContent = toolbar.shadowRoot.getElementById('1688-market-mate-toolbar');
            if (toolbarContent) {
                const buttons = toolbarContent.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.trim() === '导出表格') {
                        btn.click();
                        break;
                    }
                }
            }
        }
    """)
    tab.wait(5)
    
    print("[爬虫] 导出操作完成，等待文件下载...")
    tab.wait(5)


def check_task_canceled():
    """检查任务是否被取消"""
    if not manager.running:
        print("[爬虫] 任务被取消，准备退出")
        return True
    return False


def shop_list(server_task_id: str = None, shop_url: str = None):
    """爬取店铺商品列表（使用 1688 插件导出 Excel 方式）"""
    batch_id = gen_batch_id()
    print(f"[爬虫] 开始新批次任务: {batch_id}, 店铺URL: {shop_url}")
    save_batch(batch_id, 'running')
    
    if server_task_id:
        api.report_progress(server_task_id, "running", progress={
            "status": "opening_browser",
            "batch_id": batch_id
        })
    
    try:
        # 连接已打开的浏览器
        co = ChromiumOptions()
        co.set_local_port(9222)
        browser = Chromium(co)
        
        if check_task_canceled():
            save_batch(batch_id, 'canceled')
            return {
                "batch_id": batch_id,
                "products": [],
                "status": "canceled"
            }
        
        if server_task_id:
            api.report_progress(server_task_id, "running", progress={
                "status": "exporting_excel",
                "batch_id": batch_id
            })
        
        # 使用插件导出 Excel
        export_1688_products(browser, shop_url)
        
        if check_task_canceled():
            save_batch(batch_id, 'canceled')
            return {
                "batch_id": batch_id,
                "products": [],
                "status": "canceled"
            }
        
        if server_task_id:
            api.report_progress(server_task_id, "running", progress={
                "status": "reading_excel",
                "batch_id": batch_id
            })
        
        # 读取导出的 Excel 文件
        latest_file = get_latest_1688_file()
        
        if not latest_file:
            raise Exception("未找到导出的 Excel 文件")
        
        # 提取商品数据
        product_data_list = extract_product_data(latest_file)
        
        if check_task_canceled():
            save_batch(batch_id, 'canceled')
            return {
                "batch_id": batch_id,
                "products": [],
                "status": "canceled"
            }
        
        # 转换为标准格式
        products = []
        for idx, data in enumerate(product_data_list):
            product = {
                "task_id": f"{batch_id}_{idx}",
                "title": data.get('title', ''),
                "url": data.get('sourceUrl', ''),
                "status": "completed",
                "local_folder": latest_file,
                "priceMin": data.get('price', ''),
                "priceMax": data.get('price', ''),
                "supplierName": "",
                "supplierUrl": shop_url,
                "description": "",
                "rawData": {
                    "productId": data.get('productId'),
                    "annualSalesCount": data.get('annualSalesCount'),
                    "annualSalesOrders": data.get('annualSalesOrders'),
                    "repurchaseRate": data.get('repurchaseRate'),
                    "exportFile": latest_file
                }
            }
            products.append(product)
        
        save_batch(batch_id, 'completed', product_count=len(products))
        print(f"[爬虫] 批次 {batch_id} 完成，共爬取 {len(products)} 个商品")
        
        if server_task_id:
            api.report_result(server_task_id, batch_id, products)
        
        return {
            "batch_id": batch_id,
            "products": products
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"[爬虫] 任务执行失败: {error_msg}")
        save_batch(batch_id, 'failed')
        
        if server_task_id:
            api.report_progress(server_task_id, "failed", error=error_msg)
        
        return {
            "batch_id": batch_id,
            "products": [],
            "error": error_msg
        }


def crawl_callback(task_id: str, params: dict):
    """任务管理器回调函数"""
    shop_url = params.get('shop_url') or params.get('source_url')
    max_pages = params.get('max_pages')
    
    if not shop_url:
        print(f"[爬虫] 未提供店铺URL，任务 {task_id} 无法执行")
        return {
            "batch_id": "",
            "products": [],
            "error": "未提供店铺URL"
        }
    
    print(f"[爬虫] 开始执行任务: {task_id}")
    print(f"[爬虫] 店铺URL: {shop_url}")
    
    result = shop_list(server_task_id=task_id, shop_url=shop_url)
    return result


def main():
    print("=" * 50)
    print("  1688远程控制爬虫客户端 (Client-002)")
    print("  模式: 插件导出Excel")
    print("=" * 50)
    
    manager.set_crawl_callback(crawl_callback)
    manager.run()


if __name__ == '__main__':
    main()
