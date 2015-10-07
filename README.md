这个爬虫项目是用来爬取http://www.soopat.com 这个专利网站的数据的。

因为之前DJANGO用的比较多，这里使用了DJANGO的ORM。

数据输入为Patent/data/companies.xlsx文件，输出在output.xlsx。cell中的数据意思为: 有效专利数量\[申请中专利数量\](失效专利数量)，注意输出的2004年份实际代表的是2004年及以前的数量总和。

运行是，设置好PYTHON_PATH环境变量，具体方法为

	export PYTHON_PATH = "$PYTHON:path/to/project"