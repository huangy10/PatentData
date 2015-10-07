from tornado import httpclient, gen, ioloop

@gen.coroutine
def main():
    print 'hahaha'
    response = yield httpclient.AsyncHTTPClient().fetch('http://www.baidu.com')
    print response


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)