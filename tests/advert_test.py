import requests
from icecream import ic

# cookies = {
#     '_wbauid': '4729495271707138473',
#     'BasketUID': 'c73cc9f682ed427098bc990a846fd94a',
#     '___wbu': '2ccd174f-f476-4e61-836d-b72f1d07c658.1707138473',
#     'external-locale': 'ru',
#     'wbx-validation-key': 'ff119e40-e317-4927-b695-45c68dd50b99',
#     '__zzatw-wb': 'MDA0dBA=Fz2+aQ==',
#     'x-supplier-id-external': '96f2344d-2ca0-5ce0-b233-fea365ad86a3',
#     'cfidsw-wb': 'KESiZlHuawRMe40OiERCarvBXoXQy6Vn1d4DY9z0Mnudyx3iFx7DbgJFQB2Xm2M5ULp/CoiBL+GCfaYK3djC3rQYHgL2oZDxrWP6k+HR/pjWb5z6rJlM4ci3PSMRPUZMKX2RK525cTPUCjfCVVWcqKyq5hh7TuT/jAYYoXU=',
# }
# headers = {
#     'authority': 'cmp.wildberries.ru',
#     'accept': '*/*',
#     'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#     'authorizev3': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDg1ODg2MTQsInZlcnNpb24iOjIsInVzZXIiOiIxMzYxOTYzMDkiLCJzaGFyZF9rZXkiOiIxNyIsImNsaWVudF9pZCI6InNlbGxlci1wb3J0YWwiLCJzZXNzaW9uX2lkIjoiYzEwZDBjOGM4OGRhNDI5MGJkZjcyODA3NDA1YWU3MjQiLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTcwMTk3MTYwNSwidmFsaWRhdGlvbl9rZXkiOiI0OGU3MGQ1NTU4MDUwMGJlNjgxZWIxMDhiNzBlMzg1ODRiMTZjOWY2ZDIwNWExOGVhNDg4NWQ0YzBhY2ZiODkwIiwicGhvbmUiOiJaUTZOS2crU3N1QVpCZmhlMmNSeFNRPT0ifQ.dKRoTtJ39G8fLS6YUuoZomcp58UHFFLYQCARdtoiLGWExU3cfCWCXH7b4MAdxZGuREQ3UlmjelI0-kta_pvSW1bXX95xjW8n68o7GMTbO8oLtCq0L4e9QxyzDc71t_aa9V9QxRaWfxZkhfaQpcan5F9AgIBV2Opid9CbINJQmLPWYNKewOy90ehTlpv3DZkeuCWLP1CH5tLwA4rh_9U9cdsuXmVKSOGB-_JoIVVNUSIP8St0ESEasv7zdQ2sG27HSY8gxsRFolDZALDkzjj59BYBdYwGROtFpvfDBPJKRmxeBK-8NmSprodNBV2JlQ9-7H4AssQImUaDG6SDJuhAQQ',
#     'cache-control': 'no-cache',
#     'cookie': 'external-locale=ru; wbx-validation-key=ff119e40-e317-4927-b695-45c68dd50b99; x-supplier-id-external=96f2344d-2ca0-5ce0-b233-fea365ad86a3',
#     'referer': 'https://cmp.wildberries.ru/campaigns/list/active?pageSize=10&pageNumber=1&status=%5B4%2C9%2C11%5D&type=%5B4%2C5%2C6%2C7%2C8%2C9%5D&order=createDate&direction=desc&typePreset=All',
#     'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
#     'x-supplierid': '70825',
# }

headers = {'accept': '*/*',
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
           'authority': 'cmp.wildberries.ru',
           'authorizev3': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDg1OTI1MTAsInZlcnNpb24iOjIsInVzZXIiOiIxMzYxOTYzMDkiLCJzaGFyZF9rZXkiOiIxNyIsImNsaWVudF9pZCI6InNlbGxlci1wb3J0YWwiLCJzZXNzaW9uX2lkIjoiZmVjMTI5NjU1YzhkNDU1NzhjYmM1MTMwN2FkNDFhZTciLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTcwMTk3MTYwNSwidmFsaWRhdGlvbl9rZXkiOiIwYTM4YWNkOTQ0NDA5YzU1MGU2NzE3NGM0MjI0OTgyODUwY2Y2ZDJlNDIwNGY5NTZiMTBhYTlkMDhlY2Q5MjUwIiwicGhvbmUiOiJaUTZOS2crU3N1QVpCZmhlMmNSeFNRPT0ifQ.D9QGMkmCxNk0e4sgUTK8S2PSxILHM6YLheFS8L4-K5IZp5e8P8SDR2bbOCieAf_JSJ8pVVXW5WEK1hKMSZ_ymbQXKJJG9TMeYsatX7UUoYBsM8E4vDdKl-ts1wELtJ3zIYmusDp4rNfUBqzgboqqdNlxa1LuFfwSTevui__-uiiGnzWzKhgv6UWfGi5XRUael4towEyMfca_04q_3-t7l1xsTZ4Ny_kbHhzW-7QN6mn8HCizxYzt34co0R9XqZx6xyvOvfq-ZJS2t8LT7B_cFa158YYjH99KfrE2eQhuWj6b2Wj46yyOgagaPR5wPDkM4STuABwWtpUMJTj7zEQdfA',
           'cache-control': 'no-cache',
           'cookie': 'external-locale=ru; '
                     'wbx-validation-key=ff119e40-e317-4927-b695-45c68dd50b99; '
                     'x-supplier-id-external=7f33b867-da33-435c-b9b3-74f00020a7d6',
           'referer': 'https://cmp.wildberries.ru/campaigns/list/active',
           'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", '
                        '"Chromium";v="121"',
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"Windows"',
           'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'same-origin',
           'user-agent': 'Opera/9.80 (Windows NT 6.1; U; pl) Presto/2.7.62 Version/11.00',
           'x-supplierid': '335630'}

response = requests.get('https://cmp.wildberries.ru/api/v3/balance',
                        # cookies=cookies,
                        headers=headers)
ic(response)
