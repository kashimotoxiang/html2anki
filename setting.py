class Runoob():
    '''
    菜鸟教程参数
    '''

    def __init__(self):
        self.article = '.article-body'
        self.heading = '.article-intro h1'
        self.split = '\t'
        self.code = r'pre'
        self.others = ["¶", '\t']
        self.abstract='#content > p:nth-child(5)'


class Numpy():
    '''
    numpy manual
    '''

    def __init__(self):
        self.article = r'body'
        self.heading = [r'h1', r'h2', r'h3', r'h4']
        self.split = '\t'
        self.code = r'pre'
        self.abstract = "method"
        self.others = ["¶", '\t']


class Excel():
    '''
    excel home
    '''

    def __init__(self):

        self.article = r'vsc-initialized'
        self.heading = r'h1'
        self.split = '\t'
        self.code = r'pre'
        self.others = ["¶", '\t']
