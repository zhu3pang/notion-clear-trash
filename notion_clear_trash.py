import os
from time import sleep

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 定义重试策略
retry_strategy = Retry(
    total=5,  # 总共重试次数
    status_forcelist=[429, 500, 502, 503, 504],  # 针对这些状态码进行重试
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],  # 针对这些方法进行重试
    backoff_factor=1  # 重试间隔时间的增长因子
)

# 创建一个带有重试策略的会话
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)


# curl 'https://www.notion.so/api/v3/search' \
# -H 'content-type: application/json' \
# -H 'cookie: token_v2=v02%3Auser_token_or_cookies%3A3pnAGjgvkC1s-OGCbKE1VgruNNJvXoxFjKPjR51ujKA1nmswk7UURFuARdXIaJtFkGSc3gRUnAvYucXkQrAu4HbO-2pewoGy3HnQ4uyE11FihfoFGWIUrCxITMjXff2yWoI-' \
# --data-raw '{"type":"BlocksInSpace","query":"","filters":{"isDeletedOnly":true,"excludeTemplates":false,"navigableBlockContentOnly":true,"requireEditPermissions":false,"includePublicPagesWithoutExplicitAccess":false,"ancestors":[],"createdBy":[],"editedBy":["4c031e51-3c0b-4099-8311-a467012b0c47"],"lastEditedTime":{},"createdTime":{},"inTeams":[]},"sort":{"field":"lastEdited","direction":"desc"},"limit":20,"spaceId":"6ca3a2c6-6150-49c4-994a-1cfb109f44ee","source":"trash"}'
# curl to http request
def get_trash():
    import json

    url = "https://www.notion.so/api/v3/search"
    headers = {
        'content-type': 'application/json',
        'cookie': 'token_v2=v02%3Auser_token_or_cookies%3A3pnAGjgvkC1s-OGCbKE1VgruNNJvXoxFjKPjR51ujKA1nmswk7UURFuARdXIaJtFkGSc3gRUnAvYucXkQrAu4HbO-2pewoGy3HnQ4uyE11FihfoFGWIUrCxITMjXff2yWoI-'
    }
    data = {
        "type": "BlocksInSpace",
        "query": "",
        "filters": {
            "isDeletedOnly": True,
            "excludeTemplates": False,
            "navigableBlockContentOnly": True,
            "requireEditPermissions": False,
            "includePublicPagesWithoutExplicitAccess": False,
            "ancestors": [],
            "createdBy": [],
            "editedBy": ["4c031e51-3c0b-4099-8311-a467012b0c47"],
            "lastEditedTime": {},
            "createdTime": {},
            "inTeams": []
        },
        "sort": {
            "field": "lastEdited",
            "direction": "desc"
        },
        "limit": 100,
        "spaceId": "6ca3a2c6-6150-49c4-994a-1cfb109f44ee",
        "source": "trash"
    }
    response = http.post(url, headers=headers, data=json.dumps(data))
    data = response.json()
    print(json.dumps(data))
    return [(block["spaceId"], block["id"]) for block in data["results"]]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def delete_permanently(block_ids):
    import json

    url = "https://www.notion.so/api/v3/deleteBlocks"
    headers = {
        'content-type': 'application/json',
        'cookie': 'token_v2=v02%3Auser_token_or_cookies%3A3pnAGjgvkC1s-OGCbKE1VgruNNJvXoxFjKPjR51ujKA1nmswk7UURFuARdXIaJtFkGSc3gRUnAvYucXkQrAu4HbO-2pewoGy3HnQ4uyE11FihfoFGWIUrCxITMjXff2yWoI-'
    }
    for block_batch in chunks(block_ids, 20):
        data = {
            "blocks": [{"id": f"{x[1]}", "spaceId": f"{x[0]}"} for x in block_batch],
            "permanentlyDelete": True
        }
        http.post(url, headers=headers, data=json.dumps(data))


def official_notion_sdk_demo():
    from notion_client import Client
    notion = Client(auth=os.environ["NOTION_TOKEN"])
    list_users_response = notion.users.list()
    print(list_users_response)
    my_page = notion.databases.query(
        **{
            "database_id": "897e5a76-ae52-4b48-9fdf-e71f5945d1af",
            "filter": {
                "property": "Landmark",
                "rich_text": {
                    "contains": "Bridge",
                },
            },
        }
    )
    print(my_page)


if __name__ == "__main__":
    block_ids = get_trash()
    while block_ids:
        print(block_ids)
        delete_permanently(block_ids)
        sleep(5)
        block_ids = get_trash()
