import requests
import chardet
import lxml.html
etree = lxml.html.etree

url = 'http://www.tipdm.com' #这是一个大数据企业的网站，不是打广告！
res = requests.get(url)
res.encoding = chardet.detect(res.content)['encoding']
#print(res.text)
html = lxml.etree.HTML(res.text)
h = html.xpath('//*[@id=\"menu\"]/li/a/@href')
for i in h:
    print(i)