# -*- coding:utf-8 -*-
# Author: Zixin Wan
# Time: 2020/05/18
# Function: 生成行政区划shp文件，使用wgs-84坐标系

import requests
import json
import configparser
import shapefile
from gcj02towgs84 import gcj02towgs84

# 根据高德地图web服务的行政区查询，生成shp文件（含.prj文件），行政区级别：省/直辖市，市，区/县
class DistrictShp(object):
    def __init__(self,subdistrict=0):
        self.name=[]
        self.subdistrict=subdistrict
        self.amapWebKey=''
        self.read_ini()
        # self.amapWebKey=amapWebKey

    def read_ini(self,inipath='config.ini'):
        config = configparser.ConfigParser()
        config.read(inipath,encoding='utf-8')
        self.amapWebKey=config.get('parameter','amapWebKey')
        self.keywords=config.get('district','district')

    def getRawData(self,name):
        # 默认subdistrict为0，只显示当前行政区，不显示下级行政区
        url='http://restapi.amap.com/v3/config/district?key=%s&keywords=%s&subdistrict=%d&extensions=all'\
            %(self.amapWebKey,name,self.subdistrict)
        res=requests.get(url)
        if res.status_code == 200:
            return json.loads(res.text)
        else:
            return '0'
        
    # 由于涉及大量网络请求，速度慢，暂不用，使用计算方式
    def gcj02towgs84(self,point):
        # coordsys=gps 从GCJ-02火星坐标系转换为GPS的WGS-84坐标系
        url='https://restapi.amap.com/v3/assistant/coordinate/convert?locations=%s&coordsys=gps&key=%s'\
            %(str(point[0])+','+str(point[1]),self.amapWebKey)
        res=requests.get(url)
        if res.status_code == 200:
            return json.loads(res.text)['locations']
        else:
            return '0'

    def writePrj(self,name):
        prj=open('result/district_shp/'+name+'.prj','w')
        epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],\
            PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
        prj.write(epsg)
        prj.close()

    def getName(self,name):
        self.name.append(name)
        info=self.getRawData(name)
        if 'districts' in info['districts'][0]:
            subdistricts=info['districts'][0]['districts']
            for i in subdistricts:
                self.name.append(i['name'])

    def creatShp(self):
        for i in self.name:
            info=self.getRawData(i)
            if info != '0' and info['status'] == '1':
                name=info['districts'][0]['name']
                level=info['districts'][0]['level']
                if 'polyline' in info['districts'][0]:
                    polyline_raw=info['districts'][0]['polyline']
                else:
                    continue

                w=shapefile.Writer('result/district_shp/'+name)
                w.field('NAME','C')
                w.field('LEVEL','C')

                for polygon in polyline_raw.split('|'):
                    polygons=[]
                    for j in polygon.split(';'):
                        point=[]
                        for k in j.split(','):
                            point.append(float(k))
                        point=gcj02towgs84(point[0],point[1])
                        polygons.append(point)
                    w.poly([polygons])
                    w.record(name,level)
                
                w.close()
                self.writePrj(name)
                print(name+' .shp文件已写入。')

def main():
    # 指定子级行政区级数,默认为0，即返回当前查询的行政区，注意，只能设置0或1
    ds=DistrictShp(subdistrict=1) 

    config = configparser.ConfigParser()
    config.read('config.ini',encoding='utf-8')
    keywords=config.get('district','district')

    ds.getName(keywords)
    ds.creatShp()

if __name__ == '__main__':
    main()

