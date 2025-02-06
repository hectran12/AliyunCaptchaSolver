import aliyun

obj = aliyun.AliyunCSSolver()

#obj.solve("Please click the tiny cone.", "./data/captcha.jpg", show_result=True) # show image in window
print(obj.solve("Please click the tiny cone.", "./data/captcha.jpg")) # return x, y coordinates of the object (use for click the object)