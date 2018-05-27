import base64
import os
import time
from bs4 import BeautifulSoup
import itertools
import re
import shutil
import progressbar
import time
import functools
from lyx.common import mp_map
import setting
import subprocess
Folder_Path = r'/Users/yuxiangli/网站备份/菜鸟教程/python3'

# 是否启动关键字探测
Keywords_Detect = True
Keywords_List = ['方法', '函数', '命令', '语句']

# 1 为下载模式
# 2 为离线模式
Reference_Mode = 1


def search_filepath(folder_Path, suffixs):
    filespath = []
    for dirpath, dirs, files in os.walk(folder_Path):  # 递归遍历当前目录和所有子目录的文件和目录
        for name in files:  # files保存的是所有的文件名
            if any(os.path.splitext(name)[1] == suffix for suffix in suffixs):
                # 加上路径，dirpath是遍历时文件对应的路径
                filename = os.path.join(dirpath, name)
                filespath.append(filename)
    return filespath


class Parser(setting.Runoob):

    def __init__(self):
        super().__init__()
        self.dir = os.path.abspath("collections")
        # 创建目录
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)

    def item_join(self, items):
        result = []
        for item in items:
            result.append(item)
            result.append(self.split)
        result.pop()
        result.append('\n')
        return ''.join(result)

    def fileprocess(self, fileslist):
        bar = progressbar.ProgressBar(max_value=len(fileslist))

        # file = '/Users/yuxiangli/备份/网站资料库/devdocs/public/docs/tensorflow~python/tf/unsorted_segment_max.html'
        # fileslist=[file,file]

        def __filemap(data, bar):
            # prepare data
            i = data[0]
            filename = data[1]
            bar.update(i)

            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                # 先替换一些不需要的字符
                for item in self.others:
                    file_content = file_content.replace(item, '')

                # 解析文本
                soup = BeautifulSoup(file_content, 'html.parser')
                soup = soup.select(self.article)[0]

                # 获取标题
                heading = soup.select(self.heading)[0]
                heading = re.sub(r'\n', '', heading.get_text()
                                 ).replace(' ', '')

                # 筛选模式
                for keyword in Keywords_List:
                    if keyword in heading:
                        break
                else:
                    return

                # 获取内容
                contents = self.create_content(soup)

                # 创建摘要
                abstract = self.create_abstract(soup)

                # 合并输出
                item = self.item_join([heading, abstract, contents])
                return item
            except Exception as e:
                # 打印出最后一个文件目录，方便定位异常文件
                print("\n" + filename)
                print(e)
                print('\n\n')
                return

        filemap = functools.partial(__filemap, bar=bar)
        Contents = list(map(filemap, enumerate(fileslist)))
        Contents = [x for x in Contents if x is not None]
        return Contents

    def create_abstract(self, soup):
        # 创建摘要
        abstract = ''
        if hasattr(self, 'abstract'):
            abstract = soup.div.contents
            if abstract:
                abstract = abstract[9].get_text()
            else:
                abstract = ''
        return abstract

    def create_content(self, soup):
        # 移动媒体资源至指定目录，方便复制到anki的collections目录下
        self.__move_media_files(soup.__str__())

        # img资源重定位至更目录
        imgs = soup.find_all('img')
        for img in imgs:
            if '.jpg' in img['src']:
                newstr = img['src'].split('/')[-1]
                img['src'] = "_" + newstr
            # base64图片另存为
            elif (';base64,' in img['src']):
                base64src = img['src'].split(r';base64,')[-1]

                img_name = '_' + str(1000 * time.time()) + ".jpg"
                img['src'] = img_name

                g = open(self.dir + os.sep + img_name, "wb")
                g.write(base64.b64decode(base64src))
                g.close()

        # 代码块换行
        codes = soup.find_all(self.code)
        for code in codes:
            tmp = self.replace_newline_with_br(code.__str__())
            code.insert_before(tmp)
            code.decompose()

        # 创建内容
        content = soup.__str__().replace('\n', '')
        return content

    # def create_tags(self,soup):
        # # 创建标签
        # _tag = _heading.replace('.', "::").replace(
        #     ' ', "::").replace('(', "").replace(')', "")
        # for keyword in Keywords_List:
        #     _tag = _tag.replace(keyword, '')
        # _tag = _tag.rstrip(':')
        # _tag = _tag.replace('::::', '::')

    def __move_media_files(self, body):
        '''
        移动媒体文件至指定目录（self.dir）
        '''
        rcss = re.compile("(href|src)=\"(.*?)\"")
        filelist = rcss.findall(body)
        filelist = [x[1] for x in filelist if x[1].endswith('.css')
                    or x[1].endswith('.js') or x[1].endswith('.png')
                    or x[1].endswith('.jpg') or x[1].endswith('.jpeg')
                    or x[1].endswith('.gif')]

        for fileURL in filelist:
            filename = fileURL.split(r'/')[-1]
            filepath = Folder_Path + fileURL[2:]

            # 加下划线以符合anki规范
            filename = "_" + filename
            if filename in os.listdir(self.dir):
                continue

            if Reference_Mode == 1:
                save_path = os.path.join(self.dir, filename)

                subprocess.Popen(
                    ['wget', '-P',  save_path, fileURL])

            elif Reference_Mode == 2:
                source_path = filepath
                target_path = os.path.join(self.dir, filename)
                target_path = os.path.abspath(target_path)

                subprocess.Popen(['cp', source_path, target_path])

    def replace_newline_with_br(self, s):
        '''
        为保持代码块的可视性效果
        替换代码块中的字符串换行符"\n"为html换行符"<br>"
        '''
        lines = s.split('\n')
        pre = []
        pre.append(lines[0])
        for l in lines[1:]:
            pre.append("<br>")
            pre.append(l)
        str = ''.join(pre)
        soup = BeautifulSoup(str, 'html.parser')
        return soup


def export_link_file(dir_path):
    # 导出js和css配置文件
    path = os.path.join(dir_path, 'config.txt')
    with open(path, 'w') as f:
        js_file = [x for x in os.listdir('.') if os.path.isfile(x)
                   and os.path.splitext(x)[1] == '.js']

        css_file = [x for x in os.listdir('.') if os.path.isfile(x)
                    and os.path.splitext(x)[1] == '.css']
        for file in css_file:
            f.write('@import url(\'' + file + '\');\n')

        f.write('\n\n\n')

        for file in js_file:
            f.write('<script src=\'' + file + '\'></script>\n')


if __name__ == '__main__':
    start = time.time()

    _Parser = Parser()
    filespath = search_filepath(Folder_Path, ['.html'])
    Contents = _Parser.fileprocess(filespath)

    with open('output.txt', 'w') as f:
        for item in Contents:
            f.write(item)

    # 导出js和css配置文件
    export_link_file(_Parser.dir)

    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)
