# -*- coding:utf-8 -*-
# Author: Zixin Wan
# Time: 2020/05/20
# Function: 生成指定专题、指定城市的aoi的shp文件

import json
import requests
import math
import shapefile
import webbrowser
import configparser
from fake_useragent import UserAgent
from gcj02towgs84 import gcj02towgs84

class POIShp(object):
    def __init__(self,city,poiType,amapWebKey='eb69a25118bfbd1f06c1a9103c24df91'):
        self.city=city
        self.key=amapWebKey
        self.poiid=[]
        self.poiType=poiType

    def read_ini(self,inipath='config.ini'):
        config = configparser.ConfigParser()
        config.read(inipath,encoding='utf-8')
        # cookies=config.get('parameter','cookies')
        self.key=config.get('parameter','amapWebKey')
        self.poiType=config.get('parameter','poiType')
        # return cookies

    def getRawData(self,url):
        headers ={
            'User-Agent': UserAgent(use_cache_server=False).random,
            'Cookie': '_uab_collina=155559528978903628447463; passport_login=MjM0MjkyMjI0LGFtYXBfMTU1NDk0NDgwMzVBbTROZ3ZScmksdmdlNnpvdWh1d25qZHlrcDJzY21wdXAzZGNpaWRkdmksMTU4ODY2MjQ5NixNR013TVRVMlpUZGtOemt3WWpBeU0yTTBNelJsT0RFNFptVmtOR1F5TWprPQ%3D%3D; dev_help=FRfQXSEvKkXdez53qnNDADQ2MDMyZWMxYjYwYTE1YmEwZDFjYjk0YjdjYTE4Zjk2MWUxYzNlYTRkYzBkZTdlZTJkZTg0ZmI2MDk4OWYwZjNXFm3EvkYizgU9gvifa9d8zShm%2B3jBzHQHpkqzzI5ZADCa8QMqNZePRIxLSEoIm9HhRtgaVxoRJPYRhLmE6Id%2Bjo4LZP544sy02%2F%2FJ%2B%2FA7sH3cqzZK5jI276lMN3cs8tPngqpD4D2LAGs%2FcEpT4KxL; cna=frsFF4wtqVsCAW8SOjOSbpsM; UM_distinctid=17245eeaa373a-0c3d4a8df057cb-f313f6d-100200-17245eeaa3857; CNZZDATA1255626299=550611881-1590309744-https%253A%252F%252Fwww.baidu.com%252F%7C1590315144; guid=2189-384f-c9bc-8d07; x-csrf-token=5a211b81825fe73616c183da39e88b70; x5sec=7b22617365727665723b32223a223966663663633631366564393636666138383266613237656561336461336264434f2b7171665946454d2f466776577279716a317077453d227d; l=eBIG3Jjuv3Q68TU9BOfwourza77tSIRfguPzaNbMiOCPOa1M5DeCWZANKFTHCnGVnsc2R3oGfmNDByYUuyUICZ28nkVylJsSedLh.; isg=BEZGK1GrZJvZLzIN4Mm5hVO1lzzIp4phCmmw9TBvOGlEM-dNmDZacbiJD2__m4J5'
        }

        res=requests.get(url,headers=headers)
        info=json.loads(res.text)
        if res.status_code == 200:# and info['status'] == '1':
            return info
        elif 'url' in info:
            url='https://www.amap.com/'+info['url']
            webbrowser.open(url)
        else:
            return '0'
        
    def getPoiId(self):
        page=1
        totalPage=1000 # 最大为1000
        while page <= totalPage:
            url='https://restapi.amap.com/v3/place/text?types=%d&city=%s&offset=20&page=%d&key=%s&extensions=base&citylimit=true'\
                    %(self.poiType,self.city,page,self.key)
            info=self.getRawData(url)

            # 总页数向上取整，每次请求返回记录数20
            totalPage=math.ceil(int(info['count'])/20)

            for i in range(len(info['pois'])):
                self.poiid.append(info['pois'][i]['id'])

            page+=1
        
        print('poiid已获取完毕。共有 %d 个poi'%len(self.poiid))

    def creatShp(self):
        for poiid in self.poiid:
            url='https://www.amap.com/detail/get/detail?id=%s'%poiid
            info=self.getRawData(url)

            if 'base' in info['data']:
                pass
            else:
                continue
            name=info['data']['base']['name']
            address=info['data']['base']['address']
            city_name=info['data']['base']['city_name']
            city_adcode=int(info['data']['base']['city_adcode'])            
            x=float(info['data']['base']['x'])
            y=float(info['data']['base']['y'])
            classify=info['data']['base']['classify']
            business=info['data']['base']['business']
            
            # shape=info['data']['spec']['mining_shape']['shape']

            spec=info['data']['spec']
            if 'mining_shape' in spec:
                if 'shape' in spec['mining_shape']:
                    shape=spec['mining_shape']['shape']
                else:
                    continue
            elif 'aoi' in info['data']['base']['geodata']:
                mainpoi=info['data']['base']['geodata']['aoi'][0]['mainpoi']
                if mainpoi not in self.poiid:
                    self.poiid.append(mainpoi)
                print(name+' 不包含边界点坐标串，其父poi为 '+info['data']['base']['geodata']['aoi'][0]['name'])
                continue
            else:
                continue

            w=shapefile.Writer('result/aoi_shp/'+name)
            w.field('NAME','C')
            w.field('ADDRESS','C')
            w.field('CITY_NAME','C')
            w.field('CITY_ADCODE','N')
            w.field('LONGITUDE','F',decimal=6)
            w.field('LATITUDE','F',decimal=6)
            w.field('CLASSIFY','C')
            w.field('BUSINESS','C')

            polygon=[]
            for i in shape.split(';'):
                point=[]
                for j in i.split(','):
                    point.append(float(j))
                point=gcj02towgs84(point[0],point[1])
                polygon.append(point)
            w.poly([polygon])
            w.record(name,address,city_name,city_adcode,x,y,classify,business)
            self.writePrj(name)
            print(name+' .shp文件已写入完毕。')
            
    def writePrj(self,name):
        prj=open('result/aoi_shp/'+name+'.prj','w')
        epsg = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],\
            PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
        prj.write(epsg)
        prj.close()

def main():
    '''
    具体参考lib文件夹下的poi分类编码表，例如：
    141201 科教文化服务，高校
    110000 风景名胜，风景名胜相关，旅游景点
    110101 风景名胜，公园广场，公园
    '''
    config = configparser.ConfigParser()
    config.read('config.ini',encoding='utf-8')
    poiType=config.get('parameter','poiType')

    p=POIShp('武汉',int(poiType))  
    p.getPoiId()
    p.creatShp()

if __name__ == '__main__':
    main()
