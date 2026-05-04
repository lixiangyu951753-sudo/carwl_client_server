"""
采集任务管理平台 - Python API 调用示例
对应 web/index.html 中的所有接口调用
"""
import requests
import json

API_BASE = 'http://localhost:5001/api/v1'


def api_request(method, url, params=None, data=None):
    """统一的API请求封装"""
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request(
            method, url, headers=headers,
            params=params, json=data
        )
        return response.json()
    except Exception as e:
        return {'code': 'ERROR', 'message': str(e)}


# ==================== 统计数据 ====================

def load_stats():
    """加载统计数据（待执行、执行中、已完成、失败、在线客户端）"""
    tasks_data = api_request('GET', f'{API_BASE}/tasks', params={'page': 1, 'pageSize': 100})
    if tasks_data.get('code') == 'OK':
        tasks = tasks_data.get('data', {}).get('items', [])
        stats = {
            'pending': len([t for t in tasks if t.get('status') == 'pending']),
            'running': len([t for t in tasks if t.get('status') in ('running', 'waiting_captcha')]),
            'succeeded': len([t for t in tasks if t.get('status') == 'succeeded']),
            'failed': len([t for t in tasks if t.get('status') == 'failed']),
        }
        print(f"待执行: {stats['pending']}")
        print(f"执行中: {stats['running']}")
        print(f"已完成: {stats['succeeded']}")
        print(f"失败: {stats['failed']}")

    clients_data = api_request('GET', f'{API_BASE}/clients')
    if clients_data.get('code') == 'OK':
        print(f"在线客户端: {len(clients_data.get('data', []))}")


# ==================== 任务管理 ====================

def load_tasks(page=1, status=None):
    """加载任务列表"""
    params = {'page': page, 'pageSize': 10}
    if status:
        params['status'] = status

    data = api_request('GET', f'{API_BASE}/tasks', params=params)
    if data.get('code') != 'OK' or not data.get('data', {}).get('items'):
        print("暂无任务数据")
        return []

    tasks = data['data']['items']
    for task in tasks:
        print(f"任务ID: {task.get('taskId')}")
        print(f"  类型: {task.get('taskType')}")
        print(f"  平台: {task.get('platform', '-')}")
        print(f"  能力: {task.get('capability', '-')}")
        print(f"  状态: {task.get('status')}")
        print(f"  进度: {task.get('progress', 0)}%")
        print(f"  创建时间: {task.get('createdAt')}")
        print()

    return tasks


def cancel_task(task_id):
    """取消任务"""
    data = api_request(
        'POST', f'{API_BASE}/tasks/cancel',
        data={'taskId': task_id}
    )
    if data.get('code') == 'OK':
        print(f"任务 {task_id} 已取消")
    else:
        print(f"取消失败: {data.get('message')}")


def retry_task(task_id):
    """重试任务"""
    data = api_request(
        'POST', f'{API_BASE}/tasks/retry',
        data={'taskId': task_id}
    )
    if data.get('code') == 'OK':
        print(f"任务 {task_id} 已重试")
    else:
        print(f"重试失败: {data.get('message')}")


# ==================== 采集源管理 ====================

def load_sources(page=1, page_size=50):
    """加载采集源列表"""
    data = api_request(
        'GET', f'{API_BASE}/sources',
        params={'page': page, 'pageSize': page_size}
    )
    if data.get('code') != 'OK' or not data.get('data', {}).get('items'):
        print("暂无采集源数据")
        return []

    sources = data['data']['items']
    for source in sources:
        print(f"源ID: {source.get('sourceId')}")
        print(f"  编码: {source.get('sourceCode')}")
        print(f"  名称: {source.get('sourceName')}")
        print(f"  平台: {source.get('platform')}")
        print(f"  能力: {source.get('capability', '-')}")
        print(f"  类型: {source.get('sourceType')}")
        print(f"  状态: {source.get('status')}")
        print()

    return sources


def delete_source(source_id):
    """删除采集源"""
    data = api_request(
        'POST', f'{API_BASE}/sources/delete',
        data={'sourceId': source_id}
    )
    if data.get('code') == 'OK':
        print(f"采集源 {source_id} 已删除")
    else:
        print(f"删除失败: {data.get('message')}")


# ==================== 客户端监控 ====================

def load_clients():
    """加载在线客户端列表"""
    data = api_request('GET', f'{API_BASE}/clients')
    if data.get('code') != 'OK' or not data.get('data'):
        print("暂无在线客户端")
        return []

    clients = data['data']
    for client in clients:
        print(f"客户端ID: {client.get('client_id')}")
        print(f"  状态: {client.get('status')}")
        print(f"  当前任务: {client.get('current_task', '-')}")
        print(f"  平台: {client.get('platform', '-')}")
        print(f"  能力: {', '.join(client.get('capabilities', [])) if client.get('capabilities') else '-'}")
        print(f"  最后心跳: {client.get('last_heartbeat')}")
        print()

    return clients


# ==================== 采集结果查询 ====================

def load_items(page=1, task_id=None, keyword=None, platform=None):
    """加载采集结果列表"""
    params = {'page': page, 'pageSize': 20}
    if task_id:
        params['taskId'] = task_id
    if keyword:
        params['keyword'] = keyword
    if platform:
        params['platform'] = platform

    data = api_request('GET', f'{API_BASE}/items', params=params)
    if data.get('code') != 'OK' or not data.get('data', {}).get('items'):
        print("暂无采集结果")
        return []

    items = data['data']['items']
    for item in items:
        print(f"商品ID: {item.get('itemId', '-')}")
        print(f"  标题: {(item.get('title') or '')[:50]}")
        print(f"  平台: {item.get('platform', '-')}")
        print(f"  价格: {item.get('priceMin') or item.get('price', '-')}")
        print(f"  供应商: {item.get('supplierName') or item.get('shopName', '-')}")
        print(f"  来源链接: {item.get('sourceUrl', '-')}")
        print(f"  采集时间: {item.get('createdAt')}")
        print()

    return items


def view_item_detail(item_id):
    """查看商品详情"""
    data = api_request(
        'GET', f'{API_BASE}/items/detail',
        params={'itemId': item_id}
    )
    if data.get('code') == 'OK':
        item = data['data']
        print(f"商品ID: {item.get('itemId')}")
        print(f"标题: {item.get('title')}")
        print(f"平台: {item.get('platform')}")
        print(f"价格: {item.get('priceMin')} ~ {item.get('priceMax')}")
        print(f"供应商: {item.get('supplierName')}")
        print(f"店铺: {item.get('shopName')}")
        print(f"来源链接: {item.get('sourceUrl')}")
        print(f"主图: {item.get('mainImageUrl')}")
        print(f"描述: {(item.get('description') or '')[:200]}")
        print(f"采集时间: {item.get('createdAt')}")
        return item
    else:
        print(f"获取详情失败: {data.get('message')}")
        return None


# ==================== 创建任务 ====================

def create_task(
    task_type,
    source_id=None,
    platform=None,
    capability=None,
    shop_url=None,
    target_urls=None,
    keyword=None,
    max_items=200,
    concurrency=3,
    operator_id='admin'
):
    """
    创建采集任务

    参数:
        task_type: 任务类型 (shop_price/shop_image/single_url/batch_url/keyword)
        source_id: 采集源ID (可选，指定后自动继承平台和能力)
        platform: 平台 (1688/jd/pdd)
        capability: 能力标签 (price/image)
        shop_url: 店铺URL (shop_price/shop_image类型使用)
        target_urls: 目标链接列表 (single_url/batch_url类型使用)
        keyword: 关键词 (keyword类型使用)
        max_items: 最大采集数量
        concurrency: 并发数
        operator_id: 操作人ID
    """
    body = {
        'taskType': task_type,
        'options': {
            'maxItems': max_items,
            'concurrency': concurrency,
            'saveImagesToOss': True
        },
        'operatorId': operator_id
    }

    if source_id:
        body['sourceId'] = source_id
    if platform:
        body['platform'] = platform
    if capability:
        body['capability'] = capability
    if shop_url:
        body['shopUrl'] = shop_url
    if target_urls:
        body['targetUrls'] = target_urls
    if keyword:
        body['keyword'] = keyword

    data = api_request(
        'POST', f'{API_BASE}/tasks/create',
        data=body
    )

    if data.get('code') == 'OK':
        print(f"创建成功！")
        print(f"任务ID: {data['data']['taskId']}")
        print(f"任务编号: {data['data']['taskNo']}")
        return data['data']
    else:
        print(f"创建失败: {data.get('message')}")
        return None


# ==================== 创建采集源 ====================

def create_source(
    source_code,
    source_name,
    platform,
    capability,
    source_type,
    entry_url=None
):
    """
    创建采集源

    参数:
        source_code: 源编码 (如 src_1688_price)
        source_name: 源名称
        platform: 平台 (1688/jd/pdd)
        capability: 能力标签 (price/image)
        source_type: 源类型
        entry_url: 入口URL
    """
    body = {
        'sourceCode': source_code,
        'sourceName': source_name,
        'platform': platform,
        'capability': capability,
        'sourceType': source_type,
    }
    if entry_url:
        body['entryUrl'] = entry_url

    data = api_request(
        'POST', f'{API_BASE}/sources/create',
        data=body
    )

    if data.get('code') == 'OK':
        print(f"创建成功！")
        print(f"源ID: {data['data']['sourceId']}")
        print(f"状态: {data['data']['status']}")
        return data['data']
    else:
        print(f"创建失败: {data.get('message')}")
        return None


# ==================== 使用示例 ====================

if __name__ == '__main__':
    print("=" * 50)
    print("采集任务管理平台 - Python API 调用示例")
    print("=" * 50)

    # 1. 查看统计数据
    print("\n【查看统计数据】")
    load_stats()

    # 2. 查看任务列表
    print("\n【查看任务列表】")
    load_tasks()

    # 3. 查看采集源列表
    print("\n【查看采集源列表】")
    load_sources()

    # 4. 查看在线客户端
    print("\n【查看在线客户端】")
    load_clients()

    # 5. 查看采集结果
    print("\n【查看采集结果】")
    load_items()

    # 6. 创建采集源示例
    print("\n【创建采集源】")
    create_source(
        source_code='src_1688_image_demo',
        source_name='1688图片采集源(示例)',
        platform='1688',
        capability='image',
        source_type='shop',
        entry_url='https://xindeyi.1688.com/page/offerlist.htm'
    )

    # 7. 创建任务示例 - 手动指定平台和能力
    print("\n【创建任务 - 手动指定平台和能力】")
    create_task(
        task_type='shop_image',
        platform='1688',
        capability='image',
        shop_url='https://xindeyi.1688.com/page/offerlist.htm',
        max_items=50,
        operator_id='admin'
    )

    # 8. 创建任务示例 - 通过sourceId自动继承
    print("\n【创建任务 - 通过sourceId自动继承】")
    create_task(
        task_type='shop_image',
        source_id='src_xxx',  # 替换为实际的源ID
        shop_url='https://xindeyi.1688.com/page/offerlist.htm',
        max_items=50,
        operator_id='admin'
    )

    # 9. 取消任务示例
    # print("\n【取消任务】")
    # cancel_task('task_xxx')

    # 10. 重试任务示例
    # print("\n【重试任务】")
    # retry_task('task_xxx')

    # 11. 删除采集源示例
    # print("\n【删除采集源】")
    # delete_source('src_xxx')

    # 12. 查看商品详情示例
    # print("\n【查看商品详情】")
    # view_item_detail('item_xxx')
