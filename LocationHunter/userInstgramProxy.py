import requests
import json
import sys
import io
import random
# Discarded Method
def follow(user_id,follow_id,follow_name,csrf):
    #user_id = '4712929548'
    #follow_id = '1207862853'
    #follow_name = 'yproject_official'
    headers = {'authority': 'www.instagram.com',
               'method': 'POST',
               'path': '/web/friendships/'+follow_id+'/follow/',
               'scheme': 'https',
               'accept': 'application/json',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.8',
               'content-length': '0',
               'content-type': 'application/x-www-form-urlencoded',
               'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSCdf4610d304fa7680681644832f1a7b7c87d57470eb7ec80643b9cd6983c1d0dd%3AWEIfOwPAGg6owrh6jjUdnm1iX2r0qKpH%3A%7B%22_auth_user_id%22%3A4712929548%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712929548%3AV4ONo0Gw3gcthuueEPlfARRI4CgJAE5c%3A769a7de1010fb100f3eb32dcbcbefd1e35b3e720d15f6910210be6c4b5eade85%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1491934476.3356056213%2C%22asns%22%3A%7B%22time%22%3A1491934476%2C%2262.12.154.122%22%3A15623%7D%7D; ig_vw=1366; ig_pr=1; fbsr_124024574287414=GUdAbvCl5VjU4MVq21YWhfdAT97BNyBfBmv8aoraPEQ.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUQtNFZkSjRuWk54R1pVUmlOa0hZVmlmMzZMS0NhZVNqZGNYNjljSllTU2x5eVFCOEtURDdpbXAyQlBmU0hFWFAxeGU3dWtuZHdYTjh3bzNvbG9BZlBWazdUU2ktdGgtSGtqNXNlWmdXc0tLaW54VlNaV1A4ZWNvUGROYWl4SXVmNW11ZENidi0zR1oyWmt3aWg3SjdGc2VLalhYUGpOZXQ4OEpEV21tblZuYy1oVkwxTFNCUzNoY2NSR0luU0xtUXJFaDZpbkdMSVl5NnlNS0lIZV9UUzNtMzhaRXcweG5KaUFrVjdOWGxyRW15ejFuR19GQ2JFVF8xZ2FYNFRxcFQzS2Exa0dlRTl0dk11UTAwcUZBT1l0M2RMcV9ZUWRKTGd4ZC1fWTJKUTJ1SWxLZXNuOU11eEJuTWFBX1p2OFdTcVgyZlZiNW82dW1vUVA2Mk1nX2ZvQiIsImlzc3VlZF9hdCI6MTQ5MjAxNzQwOCwidXNlcl9pZCI6IjEwMDAwNzc2MTIyMTMyNSJ9; s_network=""; rur=FRC; csrftoken='+csrf+'; ds_user_id='+user_id,
               'origin': 'https://www.instagram.com',
               'referer': 'https://www.instagram.com/' + follow_name + '/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.8',
               'x-csrftoken': csrf,
               'x-instagram-ajax': '1',
               'x-requested-with': 'XMLHttpRequest',
               }
    print("Follow you")
    r = requests.post('https://www.instagram.com/web/friendships/'
                      +follow_id+'/follow/',headers=headers,)
    #result = json.loads(r.text)
    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')  # 改变标准输出的默认编码
    #print(r.text)
    return json.loads(r.text)
def getOneFollowee(target_id):
    each = 30
    base_url = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&'
    base_url += 'id=' + target_id + '&first=' + str(each)
    batch = {}
    headers = {
        'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSC315e0da14594818b10ec29eb55ccb35a63c4187eea8665b638252380f4e15f17%3AsNOPnIe8IV8h9Ejku940wkjCkeWg5ZXr%3A%7B%22_auth_user_id%22%3A4712929548%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712929548%3A9usbEgjU5Zou2ApMcXNYLQHNnmhDljzQ%3A70bbd9652a59aac7671bd796767a90c9223c7af6c7a9f13f151ea878d2a6c28a%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1492168111.4486522675%2C%22asns%22%3A%7B%22time%22%3A1492168472%2C%2262.12.154.122%22%3A15623%7D%7D; ds_user_id=4712929548; rur=FRC; csrftoken=osd38s1hxr8YRWlP1801zHyhicFoeM2X'
    }
    r = requests.get(base_url, headers=headers)
    batch = json.loads(r.text)
    samples = batch['data']['user']['edge_follow']['edges']
    if len(samples) == 0:
        return None
    sample = random.choice(samples)
    entity = {}
    entity['img_url'] = sample['node']['profile_pic_url']
    entity['user_id'] = sample['node']['id']
    entity['username'] = sample['node']['username']
    return entity


def getFollowees(target_id):
    each = 30
    base_url = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&'
    base_url += 'id=' + target_id + '&first=' + str(each)
    batch = {}
    headers = {
        'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSC315e0da14594818b10ec29eb55ccb35a63c4187eea8665b638252380f4e15f17%3AsNOPnIe8IV8h9Ejku940wkjCkeWg5ZXr%3A%7B%22_auth_user_id%22%3A4712929548%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712929548%3A9usbEgjU5Zou2ApMcXNYLQHNnmhDljzQ%3A70bbd9652a59aac7671bd796767a90c9223c7af6c7a9f13f151ea878d2a6c28a%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1492168111.4486522675%2C%22asns%22%3A%7B%22time%22%3A1492168472%2C%2262.12.154.122%22%3A15623%7D%7D; ds_user_id=4712929548; rur=FRC; csrftoken=osd38s1hxr8YRWlP1801zHyhicFoeM2X'
    }
    r = requests.get(base_url, headers=headers)
    batch = json.loads(r.text)
    samples = batch['data']['user']['edge_follow']['edges']
    if len(samples) == 0:
        return None
    entities  = []
    for s in samples:
      entities.append({
          'img_url' : s['node']['profile_pic_url'],
          'user_id' : s['node']['id'],
          'username' : s['node']['username']
        })
    return entities


#follow('4712929548','4937270329','waw_alfrado','qBJtwKyOLPjyHmO4o6XhobeQ8Z18VR3L')

