import base64
import os
import re
import subprocess
import time

from bs4 import BeautifulSoup

import setting


class ContentProcessor(setting.WEBTYPE):

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

                g = open(self.base_folder + os.sep + img_name, "wb")
                g.write(base64.b64decode(base64src))
                g.close()

        # 代码块换行
        codes = soup.find_all(self.code_TAG)
        for code in codes:
            tmp = self.__replace_newline_with_br(code.__str__())
            code.insert_before(tmp)
            code.decompose()

        # 创建内容
        content = soup.__str__().replace('\n', '')
        return content

    def __move_media_files(self, body):
        '''
        移动媒体文件至指定目录（self.base_folder）
        '''
        rcss = re.compile("(href|src)=\"(.*?)\"")
        filelist = rcss.findall(body)
        filelist = [x[1] for x in filelist if x[1].endswith('.css')
                    or x[1].endswith('.js') or x[1].endswith('.png')
                    or x[1].endswith('.jpg') or x[1].endswith('.jpeg')
                    or x[1].endswith('.gif')]

        for fileURL in filelist:
            filename = fileURL.split(r'/')[-1]
            filepath = self.source_folder + fileURL[2:]

            # 加下划线以符合anki规范
            filename = "_" + filename
            if filename in os.listdir(self.base_folder):
                continue

            if setting.Reference_Mode == 1:
                save_path = os.path.join(self.base_folder, filename)

                subprocess.Popen(
                    ['wget', '-P', save_path, fileURL])

            elif setting.Reference_Mode == 2:
                source_path = filepath
                target_path = os.path.join(self.base_folder, filename)
                target_path = os.path.abspath(target_path)

                subprocess.Popen(['cp', source_path, target_path])

    def __replace_newline_with_br(self, s):
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

    def create_abstract(self, soup):
        # 创建摘要
        abstract = ''
        if hasattr(self, 'abstract_TAG'):
            abstract_soup = soup.find(self.abstract_TAG)
            if abstract_soup is not None:
                if isinstance(abstract_soup, list):
                    abstract = ' '.join([x.text for x in abstract])
                else:
                    abstract = abstract_soup.text

        return abstract


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
