import requests, json, os, sys

if __name__ == '__main__':
    cookies = os.environ.get("GLADOS_COOKIE", []).split("&")
    if cookies[0] == "":
        print('未获取到COOKIE变量')
        cookies = []
        exit(0)

    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    base_headers = {
        'user-agent': UA,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'sec-ch-ua': '"Google Chrome";v="141", "Chromium";v="141", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
    }

    # 先试新端点 glados.cloud（token glados.cloud），失败再回落旧端点 glados.rocks（token glados.one）
    targets = [
        ("https://glados.cloud", "glados.cloud"),
        ("https://glados.rocks", "glados.one"),
    ]

    for cookie in cookies:
        final_line = None
        fallback_line = None
        for base, token in targets:
            try:
                h = dict(base_headers)
                h['cookie'] = cookie
                h['origin'] = base
                # 不发 referer：浏览器签到页是 no-referrer
                checkin = requests.post(base + "/api/user/checkin", headers=h, data=json.dumps({'token': token}), timeout=20)
                st_headers = {k: v for k, v in h.items() if k != 'content-type'}
                state = requests.get(base + "/api/user/status", headers=st_headers, timeout=20)
                sj = state.json()
                email = sj['data']['email']
                left = sj['data']['leftDays'].split('.')[0]
                if 'message' in checkin.text:
                    mess = checkin.json()['message']
                    line = email + '----结果--' + mess + '----剩余(' + left + ')天'
                    print(base + ' -> ' + mess, file=sys.stderr)
                    if 'Cloudflare' in mess or 'Automated' in mess:
                        if fallback_line is None:
                            fallback_line = line
                    else:
                        final_line = line
                        break
                else:
                    print(base + ' -> cookie已失效', file=sys.stderr)
                    if fallback_line is None:
                        fallback_line = 'cookie已失效'
            except Exception as e:
                print(base + ' -> 请求异常: ' + str(e)[:200], file=sys.stderr)
        print(final_line if final_line is not None else (fallback_line if fallback_line is not None else '签到失败，未获得结果'))
