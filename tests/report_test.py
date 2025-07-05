import requests
from icecream import ic

cookies = {
    'external-locale': 'ru',
    'wbx-validation-key': '4906a960-b171-47ac-84de-546c1e29a636',
    'WBTokenV3': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDg1OTI0MTQsInZlcnNpb24iOjIsInVzZXIiOiIxMzYxOTYzMDkiLCJzaGFyZF9rZXkiOiIxNyIsImNsaWVudF9pZCI6InNlbGxlci1wb3J0YWwiLCJzZXNzaW9uX2lkIjoiZmVjMTI5NjU1YzhkNDU1NzhjYmM1MTMwN2FkNDFhZTciLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTcwMTk3MTYwNSwidmFsaWRhdGlvbl9rZXkiOiIwYTM4YWNkOTQ0NDA5YzU1MGU2NzE3NGM0MjI0OTgyODUwY2Y2ZDJlNDIwNGY5NTZiMTBhYTlkMDhlY2Q5MjUwIiwicGhvbmUiOiJaUTZOS2crU3N1QVpCZmhlMmNSeFNRPT0ifQ.fOFNavlfRZCSoj9bVwAmeaKbX-OHUEjv3ulnMb258hlfhnOp1iBcglzDEYtl3x3m7UW_cLssElFvER4Dzh1-uJd3Alov_i7F9MHi7o8alQ3HeG7Lf5vBDnWXEJPZFDdWAcFSI0b3bUa3L9VoZ4_qQRqhAcmqdZKzsCmgTA3KQ2Y7jdTkjAcWFi3uoS9PNPIStEaVBCLgBf37978IZxcPEUanGjzZveXynB5t_w703oJRURvi4ED0pvESFZg4f0f7laARgRQcS7ZHTZsr6cOlnUAA-P4uVUnHiOLHRis0_f6fb8opy68GyxSPow4EAa9XeCVRWf5kM3QQusQ6WmSb3Q',
    'x-supplier-id-external': '96f2344d-2ca0-5ce0-b233-fea365ad86a3',
}

headers = {
    'authority': 'seller-weekly-report.wildberries.ru',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    # 'cookie': '_wbauid=4729495271707138473; BasketUID=c73cc9f682ed427098bc990a846fd94a; ___wbu=2ccd174f-f476-4e61-836d-b72f1d07c658.1707138473; external-locale=ru; wbx-validation-key=ff119e40-e317-4927-b695-45c68dd50b99; __zzatw-wb=MDA0dBA=Fz2+aQ==; WBTokenV3=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDczODQ5OTQsInZlcnNpb24iOjIsInVzZXIiOiIxMzYxOTYzMDkiLCJzaGFyZF9rZXkiOiIxNyIsImNsaWVudF9pZCI6InNlbGxlci1wb3J0YWwiLCJzZXNzaW9uX2lkIjoiYzEwZDBjOGM4OGRhNDI5MGJkZjcyODA3NDA1YWU3MjQiLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTcwMTk3MTYwNSwidmFsaWRhdGlvbl9rZXkiOiI0OGU3MGQ1NTU4MDUwMGJlNjgxZWIxMDhiNzBlMzg1ODRiMTZjOWY2ZDIwNWExOGVhNDg4NWQ0YzBhY2ZiODkwIiwicGhvbmUiOiJaUTZOS2crU3N1QVpCZmhlMmNSeFNRPT0ifQ.ABuXo1RjDChMFtHRzfgg1IVcPYNN7TabXbCs81ZCulX9q0QqiolMueNNeRXdp2fs889E6ybz8T0NCEPZvAV34VkE350bukpWgqFv-jazr8jII9K7a1qQCl98g_6odqxm0fFZ0aO2pVZItyrSweYSn7Lov1gtPvMxkVQxzllooXWkeg5mUlWM-7vNobi3xMhdpti-dSPRTzeFw088cXA5DiB_VVe4pVQrDPIjrWzg0UvIL3j0an5k30hVsEdDumGvNeukEhZfZfi_zlKyo3NcueCDYD-ewyYS7PuGogz8oY1mDgbBpNjs-_pfj9NLoZC0vkD2ENS56L82WpNj9DJlLw; x-supplier-id-external=96f2344d-2ca0-5ce0-b233-fea365ad86a3; cfidsw-wb=Q052ExDqRQLK+SX+IwyOce/Q28JmyHKFnySeVC6Jyyz/zxyUA6oKPcyTYMhaHD5rJm+AI/WSZTR7AjfC7IuiWuGJwqJIyrsHpe0CzfsXflFODZegNeBSBgrzk5JyzA9mggxm/5KPej97Qh44Kql4Dz757If6kgMRNE3bhy0=',
    'origin': 'https://seller.wildberries.ru',
    'referer': 'https://seller.wildberries.ru/',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

response = requests.get(
    'https://seller-weekly-report.wildberries.ru/ns/realization-reports/suppliers-portal-analytics/api/v1/new-balance-date',
    cookies=cookies,
    headers=headers,
)
ic(response)
ic(response.text)