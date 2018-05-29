import itertools
import os
import re
import shutil
import time

from bs4 import BeautifulSoup
from tqdm import tqdm

import setting
from process_content import ContentProcessor, export_link_file


def escape_exception(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as e:
            # 打印出最后一个文件目录，方便定位异常文件
            # print("\n" + filename)
            print(e)
            print('\n\n')
            return


class Meta():
    soup = None

    title_soup = None
    title_str = None

    content = None
    content_soup = None

    abstract = None
    result = None

    content_processor = ContentProcessor()

    def __init__(self, title_soup, content_soup):
        title_soup = title_soup
        title_str = title_soup.find(text=True)
        if len(title_str) != 0:
            title_str = re.sub(r'\n', '', title_str).replace(' ', '')

        self.title_str = title_str
        self.title_soup = title_soup
        self.content_soup = content_soup

    def create_meta(self):
        def item_join(items):
            result = []
            for item in items:
                result.append(item)
                result.append('\t')
            result.pop()
            result.append('\n')
            return ''.join(result)

        # 获取内容
        self.content = self.content_processor.create_content(self.content_soup)

        # 创建摘要
        self.abstract = self.content_processor.create_abstract(self.content_soup)

        # 合并输出
        self.result = item_join([self.title_str, self.abstract, self.content])


class Parser(setting.WEBTYPE):
    base_folder = None
    source_folder = None

    file_pool = None

    def __init__(self, source_folder, suffixs=None):
        super().__init__()
        self.base_folder = os.path.abspath("collections")
        self.source_folder = source_folder
        self.file_pool = self.search_filepath(source_folder, suffixs)

        # 创建目录
        if os.path.exists(self.base_folder):
            shutil.rmtree(self.base_folder)
        os.makedirs(self.base_folder)

    def search_filepath(self, folder_path, suffixs=None):
        file_pool = []
        for dirpath, dirs, files in os.walk(folder_path):  # 递归遍历当前目录和所有子目录的文件和目录
            for name in files:  # files保存的是所有的文件名
                if suffixs:
                    # 需要后缀
                    if any(os.path.splitext(name)[1] == suffix for suffix in suffixs):
                        # 加上路径，dirpath是遍历时文件对应的路径
                        filespath = os.path.join(dirpath, name)
                    else:
                        continue
                else:
                    # 不需要后缀
                    filespath = os.path.join(dirpath, name)
                file_pool.append(filespath)
        return file_pool

    def get_soup(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()
        # 先替换一些不需要的字符
        for item in self.others_TAG:
            file_content = file_content.replace(item, '')

        # 解析文本
        soup = BeautifulSoup(file_content, 'html.parser')
        soup = soup.select(self.article_TAG)
        if isinstance(soup, list):
            soup = soup[0]

        return soup

    def get_meta(self, soup):
        title_soups_pool = soup.select(self.title_TAG)

        meta_list = []

        for title_soup in title_soups_pool:
            content_tag_list = []

            next_tags = title_soup.nextSibling

            while True:
                if next_tags in title_soups_pool or next_tags is None:
                    break
                else:
                    content_tag_list.append(next_tags)
                next_tags = next_tags.nextSibling

            content_str = [x.__str__() for x in content_tag_list]
            content_str = ''.join(content_str)
            content_soup = BeautifulSoup(content_str, 'html.parser')
            meta = Meta(title_soup, content_soup)
            meta_list.append(meta)
        return meta_list

    def process_pages(self, filename):
        soup = self.get_soup(filename)
        meta_list = self.get_meta(soup)

        # 筛选模式
        if setting.Keywords_Detect and len(meta_list) != 0:
            result = []
            for meta in meta_list:
                for keyword in setting.Keywords_List:
                    if keyword in meta.title_str:
                        break
            else:
                result.append(meta)
        else:
            result = meta_list

        list(map(lambda x: x.create_meta(), result))

        return result

    def start(self):
        Contents = list(map(self.process_pages, tqdm(self.file_pool)))
        Contents = itertools.chain(*Contents)
        Contents = [x for x in Contents if x is not None]
        return Contents


if __name__ == '__main__':
    start = time.time()

    parser = Parser(setting.Folder_Path)
    Contents = parser.start()

    print('写入文件')
    with open('output.txt', 'w') as f:
        for item in Contents:
            f.write(item.result)

    # 导出js和css配置文件
    export_link_file(parser.base_folder)

    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)
