# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 20:09:01 2018

@author: bcd
"""
import itchat#获取微信信息
import matplotlib.pyplot as plt
import pandas as pd
import re
import jieba
import jieba.analyse#从一句话中找出tags
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
import PIL.Image as Image#绘制词云图要用的
import snownlp#分析中文情感
import matplotlib.ticker as mtick   #做比例图的时候y轴显示比例
import os
from os import listdir#拼接头像的时候要用
import TencentYoutuyun as ty
from os import listdir
import math

def explode(label,target='female'):#做男女比例饼形图的时候突出显示女性
    if label == target: 
        return 0.1
    return 0
 
class wechat(object):
    def __init__(self):
        itchat.auto_login()#这种登录方式需要先运行一下，出现key error:url然后重启spyder,还有二维码要扫不止1次（它会自动用画图打开几个QR.png）才能登陆，否则显示超时
        self.friends =itchat.get_friends(update=True)[0:]#爬取自己好友相关信息， 返回一个contactlist type文件
        plt.rcParams['font.sans-serif']=['SimHei']#这两行解决中文显示方块问题
        plt.rcParams['font.serif'] = ['SimHei']
        #print(self.friends)
        self.username=self.friends[0]['NickName']
        self.total = len(self.friends[1:])#第一个是自己
    def get_var(self,var):#
        variable = []
        for i in self.friends:
            value = i[var]
            variable.append(value)
        return variable
    def save_info(self):#调用函数得到各变量，并把数据存到文件中，保存到d盘
        self.NickName= self.get_var("NickName")
        self.Sex = self.get_var('Sex')
        self.Province = self.get_var('Province')
        self.City = self.get_var('City')
        self.Signature = self.get_var('Signature')
        self.data = {'NickName': self.NickName, 'Sex': self.Sex, 'Province': self.Province,'City': self.City, 'Signature': self.Signature}
        frame = pd.DataFrame(self.data)
        with open("d:/friends_info.xlsx","w+") as fp:
            frame.to_excel("d:/friends_info.xlsx",index=True)
 
    def sex_ratio(self):
        self.male = self.female = self.other = 0
        for i in self.friends[1:]:#friends[0]是自己的信息，所以要从friends[1]开始
            sex = i["Sex"]
            if sex == 1:
                self.male += 1
            elif sex == 2:
               self.female += 1
            else:
                self.other +=1
        #打印出自己的好友性别比例
        print("男性好友： %.2f%%" % (float(self.male)/self.total*100) + "\n" +"女性好友： %.2f%%" % (float(self.female) / self.total * 100) + "\n" +"不明性别好友： %.2f%%" % (float(self.other) /self. total * 100))
        #绘制饼形图
        labels= ['male','female','other']
        clabels=["男性","女性","其他"]
        quants= [self.male,self.female,self.other]
        colors= ['lightskyblue','pink','yellow']
        expl=list(map(explode,labels))#类似ufunc对labels里面每一个元素操作,返回iretator
        plt.figure(1,figsize=(6,6))
        plt.pie(quants,explode=expl,colors=colors,labels=clabels,autopct='%1.1f%%',pctdistance=0.5,shadow=True)
        plt.title(self.username+'微信好友性别比例')
        plt.savefig("d:/sex_ratio.jpg",dpi=200) #一定要在show之前save
        plt.show()
        
    def sig_cloud(self):
        self.siglist = []
        with open("d:/signature.txt","w+",encoding="utf-8") as fp:
            for i in self.friends:
                signature = i["Signature"].strip().replace("span","").replace("class","").replace("emoji","").replace(' ','\n')
                rep = re.compile("1f\d+\w*|[<>/=]")
                signature = rep.sub("", signature)
                self.siglist.append(signature)
                fp.writelines(signature)
            fp.write('------------------------------------------------------')
            text = "".join( self.siglist)
            fp.writelines(text)
        wordlist = jieba.cut(text, cut_all=True)
        self.word_space_split = " ".join(wordlist)
        with open("d:/word_space_split.txt","w+",encoding="utf-8") as fp:
            fp.writelines(self.word_space_split.replace(' ','\n'))
     
        #开始画词云图
        plt.figure(2)
        coloring = np.array(Image.open("D:/alice_mask.png"))
        my_wordcloud = WordCloud(background_color="aliceblue",scale=8,max_words=2000,mask=coloring,max_font_size=60,random_state=42,font_path="C:\Windows\Fonts\SimHei.ttf").generate(self.word_space_split)
        image_colors = ImageColorGenerator(coloring)
        plt.imshow(my_wordcloud,interpolation='bilinear')
        plt.axis("off")
        plt.savefig("d:/sig_cloud.jpg",dpi=200)
        plt.show()
        
    def analyseSignature(self):
        signatures = ''
        emotions = []
        pattern = re.compile("1f\d.+")
        for i in self.Signature:
            if len(i)>0:
                nlp = snownlp.SnowNLP(i)
                emotions.append(nlp.sentiments)
                signatures += ' '.join(jieba.analyse.extract_tags(i,5))
        with open('d:\signatures.txt','w+',encoding='utf-8') as fp:
             fp.write(signatures)           
        # 情感分析
        plt.figure(3)
        self.good=list(filter(lambda x:x>0.66,emotions))
        self.normal=list(filter(lambda x:x>=0.33 and x<=0.66,emotions))
        self.bad=list(filter(lambda x:x<0.33,emotions))
        count_good = len(self.good)
        count_normal = len(self.normal)
        count_bad = len(self.bad)
        labels = ['负面消极','中性','正面积极']
        values = (count_bad,count_normal,count_good)
        plt.rcParams['axes.unicode_minus'] = False
        plt.xlabel('情感判断')
        plt.ylabel('频数')
        plt.xticks(range(3),labels)
        plt.legend(loc='upper right',)
        plt.bar(range(3), values,color = ['dodgerblue','yellowgreen','lightpink'])
        plt.title(self.username+'的微信好友签名信息情感分析')
        plt.savefig("d:/emotion.jpg",dpi=200)
        plt.show()

    def analyseLocation(self):
        d={}    
        for i in self.Province:
            if i not in d.keys() and len(i)>0:
                d[i]=self.Province.count(i)
        with open('d:\province.txt','w+',encoding='utf-8') as fp:
             fp.writelines(d)      
        p1=[]
        p2=[]
        n1=[]
        n2=[]
        for i in d.keys():
            p1.append(i)
            n1.append(d[i])
            for j in self.friends:
                if j.Province==i and j.City not in p2:
                    p2.append(j.City)
                    n2.append(self.City.count(j.city))
        plt.figure(5,figsize=(20,20))
        plt.subplot(211)
        plt.bar(range(len(p1)), n1,color=['red','pink','orange','yellow'],tick_label=p1)  
        plt.title(self.username+'好友所在省的分布')
        plt.subplot(212)
        plt.bar(range(len(p2)), n2,color=['green','blue','purple'],tick_label=p2)  
        plt.title(self.username+'好友所在城市的分布')
        plt.savefig("d:/location.jpg",dpi=200)
        plt.show()
        
    def headimage_glue(self):
        user=self.username
        os.mkdir(user)#不能存在同名文件夹
        num = 0
        for i in self.friends:
        	img = itchat.get_head_img(userName=i["UserName"])
        	fileImage = open(user + "/" + str(num) + ".jpg",'wb')
        	fileImage.write(img)
        	fileImage.close()
        	num += 1
        pics = listdir(user)
        numPic = len(pics)
        eachsize = int(math.sqrt(float(640 * 640) / numPic))
        numline = int(640 / eachsize)
        toImage = Image.new('RGBA', (640, 640))     
        x = 0
        y = 0       
        for i in pics:
        	try:
        		#打开图片
        		img = Image.open(user + "/" + i)
        	except IOError:
        		print("Error: 没有找到文件或读取文件失败")
        	else:
        		#缩小图片
        		img = img.resize((eachsize, eachsize), Image.ANTIALIAS)
        		#拼接图片
        		toImage.paste(img, (x * eachsize, y * eachsize))
        		x += 1
        		if x == numline:
        			x = 0
        			y +=1
        toImage.save(user + '.jpg')
if __name__=="__main__":
    my=wechat()
    my.save_info()
    print("username:",my.username)
    my.sex_ratio()#运行一次最好只调用一个函数，要不然会很慢
    my.sig_cloud()
    my.analyseSignature()
    my.analyseLocation()
    my.headimage_glue()


