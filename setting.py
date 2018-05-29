Folder_Path = r'/Users/yuxiangli/网站备份/spacy.io/untitled folder'

# 是否启动关键字探测
Keywords_Detect = False
Keywords_List = ['方法', '函数', '命令', '语句']

# 1 为下载模式
# 2 为离线模式
Reference_Mode = 1


class Runoob():
    '''
    菜鸟教程参数
    '''

    def __init__(self):
        self.article_TAG = '.article-body'
        self.title_TAG = '.article-intro h1'
        self.code_TAG = r'pre'
        self.abstract_TAG = '#content > p:nth-child(5)'
        self.others_TAG = ["¶", '\t']


class Numpy():
    '''
    numpy manual
    '''

    def __init__(self):
        self.article_TAG = r'body'
        self.title_TAG = [r'h1', r'h2', r'h3', r'h4']
        self.code_TAG = r'pre'
        self.abstract_TAG = "method"
        self.others_TAG = ["¶", '\t']


class Excel():
    '''
    excel home
    '''

    def __init__(self):
        self.article_TAG = r'vsc-initialized'
        self.title_TAG = r'h1'
        self.code_TAG = r'pre'
        self.others_TAG = ["¶", '\t']


class Spacy():
    '''
    excel home
    '''

    def __init__(self):
        self.article_TAG = r'article'
        self.title_TAG = r'.u-heading-2'
        self.code_TAG = r'pre'
        self.others_TAG = ["¶", '\t']
        self.abstract_TAG = 'p'


WEBTYPE = Spacy
