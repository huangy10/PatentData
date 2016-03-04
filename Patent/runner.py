# !coding=utf-8
import os
import xlrd
import xlwt
import datetime
import re
import time
import random
import sys

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils import timezone
from django.db import models
from tornado import httpclient, gen, ioloop, queues
from bs4 import BeautifulSoup
sys.path.extend([os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, os.pardir))])
# sys.path.extend(['/Users/Lena/Project/Python/Spider/PatentData'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PatentData.settings')
application = get_wsgi_application()

from Patent.models import Company, Patent

__author__ = 'Woody Huang'
__version__ = '1.0.0'


default_file_path = os.path.join(settings.BASE_DIR, 'Patent', 'data', 'companies.xlsx')
base_url = 'http://www.soopat.com/Home/Result?SearchWord=%s&&FMZL=Y&SYXX=Y&WGZL=Y'
companies_pool = queues.Queue()

total_companies_num = 0
fetched_companies_num = 0

user_agents = ['Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50,'
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
               'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',]


def load_company_list(file_path, company_name_col_index=2, skip_rows=1):
    """ This function load companies information from the .xlsx file,
     and save them to the database
    """
    data = xlrd.open_workbook(file_path).sheets()[0]
    nrows = data.nrows
    new_company = 0
    for row_index, company_name in enumerate(data.col_values(company_name_col_index)[skip_rows:]):
        _, created = Company.objects.get_or_create(name=company_name)
        if created:
            new_company += 1

    print '{0}个公司的数据已经被存入数据库，其中新建的有{1}个'.format(nrows-1, new_company)


@gen.coroutine
def parse_data_for_html(html_doc, company):
    """ This utility function parse useful data from the html text
    """
    soup = BeautifulSoup(html_doc, 'html.parser')
    # 首先检查是否遇到了验证码问题
    check = soup.find_all('img', {'src': '/Account/ValidateImage'})
    if check is not None and len(check) > 0:
        print '~~~~~~~~~~遇到验证码问题'
        raise gen.Return(-1)
    patent_blocks = soup.find_all('div', {'class': 'PatentBlock', 'style': None})
    for patent_block in patent_blocks:
        name = patent_block.find('input', {'name': 'cb'})['mc']
        patent_key = patent_block.h2.font.text
        patent_type = {u'[发明]': 'FM', u'[外观]': 'WG', u'[实用新型]': 'SY'
                       }[re.search(r'\[.*\]', patent_key).group()]
        note = patent_block.h2.a.find('font', {'size': -1}).text
        status = dict(
            stateicoinvalid='invalid',
            stateicovalid='valid',
            stateicopending='applying'
        )[patent_block.h2.div['class'][-1]]
        a_tag = patent_block.span.find_all('a')
        company_name = a_tag[0].text
        apply_at = re.search(r'\d\d\d\d-\d\d-\d\d', patent_block.span.text).group()
        category = a_tag[1].text
        abstract = patent_block.find('span', {'class': 'PatentContentBlock'}).text
        yield gen.Task(save_patent_to_database, dict(
            name=name,
            apply_at=apply_at,
            abstract=abstract,
            type=patent_type,
            status=status,
            company=company,
            category=category,
            note=note
        ))
    raise gen.Return(len(patent_blocks))


def save_patent_to_database(data, callback):
    # first check whether the given pattern already exist
    if Patent.objects.filter(note=data['note']).exists():
        print u'专利%s已存在' % data['note']
        return callback()
    Patent.objects.create(
        name=data['name'],
        apply_at=datetime.datetime.strptime(data['apply_at'], '%Y-%m-%d'),
        abstract=data['abstract'],
        type=data['type'],
        status=data['status'],
        company=data['company'],
        category=data['category'],
        note=data['note']
    )
    print u'存入专利%s' % data['note']
    return callback()


@gen.coroutine
def search_for_company(company, skip=0):
    """ Search for the given company name, save the result to the database through ORM of django
     返回是一个Turple:
      (是否完成，完成的数量，未完成原因)
    """
    print u'->开始搜索：%s' % company.name
    fetched_patent = skip
    start_url = base_url % company.name.strip()
    # cookie = 'patentids=; domain=.soopat.com; expires=%s GMT; path=/' %\
    #          (timezone.now() + datetime.timedelta(seconds=60)).strftime('%a, %d-%b-%Y %H-%M-%S')
    cookie = 'lynx-randomcodestring=; patentids='
    client = httpclient.AsyncHTTPClient()
    while True:
        if fetched_patent > 0:
            request_url = start_url + '&PatentIndex=%s' % fetched_patent
        else:
            request_url = start_url
        print u'开始发送访问请求：%s' % request_url

        print 'cookie::' + cookie
        request = httpclient.HTTPRequest(url=request_url,
                                         headers={'Cookie': cookie,
                                                  'User-Agent': random.choice(user_agents)},
                                         follow_redirects=False,)
        response = yield client.fetch(request, raise_error=False)
        if response.code == 200:
            new_patents = yield parse_data_for_html(response.body, company)
            if 0 <= new_patents < 10:
                if new_patents == 0:
                    print u'未能发现新的专利'
                break
            elif new_patents == -1:
                print u'正在退出搜索: %s' % fetched_patent
                # 如果遇到了验证码问题，返回进行休眠，通过返回告知上层目前进度
                raise gen.Return((False, fetched_patent, 'authenticate code'))
            fetched_patent += new_patents
            sleep_time = random.uniform(2, 10)
            print '正常工作间隔%s' % sleep_time
            time.sleep(sleep_time)
            print response.headers
            cookie = response.headers.get('Set-Cookie', '')
        elif response.code == 500:
            print '遇到500错误，完成对当前条目的搜索'
            break
        else:
            print '出现其他返回状态代码：%s -> %s' % (response.code, response.headers.get('Location', ''))
            print response.body
            time.sleep(10)
    client.close()
    raise gen.Return((True, fetched_patent, None))


@gen.coroutine
def main():
    # 读取一些配置信息
    company_num = Company.objects.all().count()
    patent_num = Patent.objects.all().count()
    if company_num > 0 or patent_num > 0:
        print("数据库中已有%s家公司的%s条专利数据" % (company_num, patent_num))
        print("\n\n")
        clear_old_data = raw_input("是否清除已有的数据(y/[n])")
        if clear_old_data in ["y", "Y"]:
            Company.objects.all().delete()
            Patent.objects.all().delete()
            print("已清除原有数据!")
            print("\n\n\n\n\n")
    global total_companies_num
    # first make sure that all the company data are loaded
    print '###############爬虫启动！##################'
    print '从Excel文件中载入公司数据'
    default_path = os.path.join(settings.BASE_DIR, 'Patent', 'data', 'companies.xlsx')
    path_option = raw_input("默认输入文件路径是%s,是否使用其他输入文件(y/[n])")
    if path_option in ["y", "Y"]:
        default_path = raw_input("输入文件路径:").strip()
    load_company_list(default_path)
    print '载入完成'
    # Since the company number is not so large, load them into the queue
    print '将数据载入队列等待处理'

    for c in Company.objects.filter(checked=False):
        yield companies_pool.put(c)
        total_companies_num += 1

    print '载入完成，开始爬取数据，本次需要爬取的公司总数为: %s' % total_companies_num

    @gen.coroutine
    def worker(worker_id):
        global fetched_companies_num

        print 'WORKER %s START!' % worker_id
        finished = True
        skip = 0
        code_error_times = 0        # 连续发生验证码阻碍的次数
        while True:
            if finished:
                next_company = yield companies_pool.get()
                skip = Patent.objects.filter(company=next_company).count()
            finished, skip, reason = yield search_for_company(next_company, skip=skip)
            if not finished:
                if reason == 'authenticate code':
                    code_error_times += 1
                    sleep_time = min(random.uniform(10, 100) * code_error_times, 400)
                    print u'】WORKER %s 进入休眠，本轮休眠时间为：%s' % (worker_id, sleep_time)
                    time.sleep(sleep_time)  # If fails, sleep a random time
                    print u'】WORKER %s 恢复工作' % worker_id
            else:
                code_error_times = 0
                fetched_companies_num += 1
                next_company.checked = True
                next_company.save()
                print u'完成对【%s】的专利数据查询，目前进度%s/%s' % (
                    next_company.name, fetched_companies_num, total_companies_num)
                companies_pool.task_done()
                time.sleep(10)
    for i in range(1):
        worker(i)
    yield companies_pool.join()
    print '###############爬虫停止！##################'
    print '##########数据导出到output.xlsx############'
    write_database_to_excel()


def write_database_to_excel():
    book = xlwt.Workbook()
    sheet = book.add_sheet(u'专利数据', cell_overwrite_ok=True)
    companies = Company.objects.filter(checked=True)

    def get_count_expression_for_patent(company, year, category):
        if year >= 2005:
            pre_filter = Patent.objects.filter(apply_at__lt=('%s-01-01' % (year+1)),
                                               apply_at__gte=('%s-01-01' % year))\
                .filter(company=company, type=category)
        else:
            pre_filter = Patent.objects.all()\
                .filter(apply_at__lt=('%s-01-01' % (year + 1))).filter(company=company, type=category)
        valid = pre_filter.filter(status='valid').count()
        applying = pre_filter.filter(status='applying').count()
        invalid = pre_filter.filter(status='invalid').count()
        result = ''
        if valid > 0:
            result += str(valid)
        if applying > 0:
            result += '[%s]' % applying
        if invalid > 0:
            result += '(%s)' % invalid
        return result

    sheet.write(0, 0, u'序号')
    sheet.write(0, 1, u'企业名称')
    for (index, year) in zip(range(2, 35, 3), range(2004, 2015)):
        sheet.write(0, index, 'FM%s' % year)
        sheet.write(0, index+1, 'SY%s' % year)
        sheet.write(0, index+2, 'WG%s' % year)

    for k, c in enumerate(companies):
        print 'Writing[%s]: %s' % (k, c.name)
        i = k + 1
        sheet.write(i, 0, i)                # 序号
        sheet.write(i, 1, c.name)           # 公司名称
        for (index, year) in zip(range(2, 35, 3), range(2004, 2015)):
            sheet.write(i, index, get_count_expression_for_patent(c, year, 'FM'))
            sheet.write(i, index+1, get_count_expression_for_patent(c, year, 'SY'))
            sheet.write(i, index+2, get_count_expression_for_patent(c, year, 'WG'))
    print 'finished'
    book.save(os.path.join(settings.BASE_DIR, 'Patent', 'data', 'output.xlsx'))


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)

