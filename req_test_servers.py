import requests
r = requests.post('http://localhost:5000/api/tasks', json={
    'instruction': 'start_crawl',
    'params': {'shop_url': 'https://xindeyi.1688.com/page/offerlist.htm', 'max_pages': 2}
})
print(r.json())