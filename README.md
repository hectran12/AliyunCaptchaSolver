# Aliyun Captcha Solver

Solver aliyun captcha

## Installation
下载项目后，运行以下命令来安装依赖库。
```
pip install -r requirements.txt
```

## Usage
函数 solve 有两种返回方式：
1. 显示图片。

![demo](https://github.com/hectran12/AliyunCaptchaSolver/blob/main/github/img/image.jpg)


3. 返回坐标 (x, y)。

   
![demo](https://github.com/hectran12/AliyunCaptchaSolver/blob/main/github/img/xy.png)



```py
import aliyun

obj = aliyun.AliyunCSSolver()

#obj.solve("Please click the tiny cone.", "./data/captcha.jpg", show_result=True) # show image in window
print(obj.solve("Please click the tiny cone.", "./data/captcha.jpg")) # return x, y coordinates of the object (use for click the object)
```
在浏览器上进行测试。
```py
import aliyun, time, requests
from playwright.sync_api import sync_playwright


def download_image(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)    
    


"""
    PHẢI CÓ TUT THÌ MỚI QUA ĐƯỢC NHÉ, DÙ CÓ GIẢI ĐÚNG THÌ VẪN BỊ "SIGNATURE FAILED" :)))
    ĐOẠN CODE CHỈ MANG TÍNH CHẤT HỌC HỎI.

"""

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()

    page.goto("https://cloud.vmoscloud.com/buy")

    page.wait_for_selector('input[placeholder="Please enter your email address"]')
    page.click('span:has-text("Verification code login")')


    page.fill('input[placeholder="Please enter your email address"]', "tronghoadeptrai2008@gmail.com")



    time.sleep(5)

    page.wait_for_selector('#get-captcha-code')
    page.click('#get-captcha-code')

    question = page.inner_text('#aliyunCaptcha-question')
    image_src = page.evaluate('() => document.querySelector("#aliyunCaptcha-img").src')

    print("Question: ", question)
    print("Image src: ", image_src)


    download_image(image_src, "./data/captcha.jpg")
    print("Captured image saved to ./data/captcha.jpg")

    ali_obj = aliyun.AliyunCSSolver()
    x, y = ali_obj.solve(question, "./data/captcha.jpg", show_result=False)
    


    page.evaluate(f'''
        (function() {{
            function clickAtCoordinates(x, y) {{
                const element = document.querySelector("#aliyunCaptcha-img");
                if (!element) {{
                    console.error("Element #aliyunCaptcha-img not found");
                    return;
                }}
                const rect = element.getBoundingClientRect();
                const event = new MouseEvent("click", {{
                    bubbles: true,
                    cancelable: true,
                    clientX: rect.left + x,
                    clientY: rect.top + y,
                    view: window
                }});
                element.dispatchEvent(event);
            }}
            window.clickAtCoordinates = clickAtCoordinates;
        }})();
    ''')

    page.evaluate(f'window.clickAtCoordinates({x}, {y})')
    print("Captcha click successfull")
    input()


    browser.close()


```

## Contributing
欢迎提交 Pull Request。如果是重大更改，请先创建 Issue 讨论你想修改的内容。

请确保适当更新测试。

注意：也许我并不在意，因为这是我的学习项目。我只是随便写着玩，所以并没有打算持续开发…… :D

## License

[MIT](https://choosealicense.com/licenses/mit/)
