#!/usr/bin/env python
#    Copyright (C) 2018  Takuya Chaen
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import urllib.request
import re
import time
import sys
import posixpath
import math
from datetime import datetime

class TmblrPix():

    api_url	= 'http://#domain#/api/read?type=photo&num=#num#&start=#start#'
    get_num_per_one = 50
    headers = { "User-Agent" :  "Mozilla/4.0" }

    def get_element_one(self,start,end,searchtext):
        retvalue = ""
        i = 0
        while i >= 0:
            startposition = searchtext.find(start)
            if startposition > 0:
                searchtext = searchtext[startposition+len(start):]
                endposition = searchtext.find(end)
                if endposition > 0:
                    getelement = searchtext[0:endposition]
                    retvalue = getelement
                    return retvalue
            else:
                break
        return retvalue

    def create_folder(self,folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def get_image_num(self,domain):
        tumblr_site = self.api_url.replace("#domain#",domain)
        tumblr_site = tumblr_site.replace("#num#",'1')
        tumblr_site = tumblr_site.replace("#start#",'0')
        req = urllib.request.Request(tumblr_site, None, self.headers)
        response = urllib.request.urlopen(req)
        charset = response.headers.get_content_charset()
        if charset==None:
            charset = "utf-8"
        get_data = response.read().decode('utf-8')
        get_total_num = self.get_element_one('total="','"',get_data)
        return get_total_num

    def get_image_url(self,domain,start,number):
        tumblr_site = self.api_url.replace("#domain#",domain)
        tumblr_site = tumblr_site.replace("#num#",str(number))
        tumblr_site = tumblr_site.replace("#start#",str(start))
        req = urllib.request.Request(tumblr_site, None, self.headers)
        response = urllib.request.urlopen(req)
        get_data = response.read().decode('utf-8')
        get_regex = '<photo-url max-width="1280">(.+?)</photo-url>'
        url_list = re.findall(get_regex,str(get_data))
        return url_list

    def get_url_list_with_domain(self,get_domain,max_num):
        all_list = []
        total_num = self.get_image_num(get_domain)
        total_num = int(total_num)
        if total_num < 1:
            return
        get_num = float(total_num) / self.get_num_per_one
        get_num = int(math.ceil(get_num))
        self.create_folder(get_domain)
        current_offset = 0
        for i in range(get_num):
            time.sleep(1)
            if i == max_num:
                return all_list
            get_list = self.get_image_url(get_domain,current_offset,self.get_num_per_one)
            if len(get_list) == 0:
                return all_list
            for image_url in get_list:
                all_list.append(image_url)
            current_offset = current_offset + self.get_num_per_one
        return all_list

    def write_to_file(self,url_list,get_domain):
        if len(url_list) > 0:
            set_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            file_name = get_domain + '/' + set_time + '_url.txt'
            try:
                f = open(file_name , 'w')
                for set_url in url_list:
                    f.writelines(set_url + "\n")
                f.close()
            except:
                err = 1

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        get_domain = args[1]
        max_page = args[2]
        max_page = int(max_page)
        tumblrpix = TmblrPix()
        all_url = tumblrpix.get_url_list_with_domain(get_domain,max_page)
        tumblrpix.write_to_file(all_url,get_domain)
    else:
        print("usage: python3 tumblrpicdump.py download_account.tumblr.com max_num")
        print("   ex: python3 tumblrpicdump.py download_account.tumblr.com 100")
