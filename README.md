# 爬取数据生成shp文件

## 1.功能简介

共有两大功能，一个功能是根据高德地图web服务API获取行政区划坐标串，写入行政区shp文件；另一个功能是根据高德地图的接口获取poi坐标串，写入aoi(area of interest)的shp文件。

## 2.文件说明

**lib文件夹**，包含两个xls文件，分别是高德地图的城市编码表和POI分类编码表。

**result/district_shp文件夹**，用于存储生成的行政区shp文件。

**result/aoi_shp文件夹**，用于存储生成的aoi的shp文件。

**config.ini文件**，配置文件，填写高德地图web服务的key；填写要爬取的poi的类别编码；填写爬取城市的adcode。

**getPoiShp.py文件**，生成指定专题、指定城市的aoi的shp文件。

**getDistrictShp.py文件**，生成行政区划shp文件。

**gcj02togps84.py文件**，高德地图使用的是GCJ-02坐标系，用此py文件转换为WGS-84坐标系。

> GCJ-02是由中国国家测绘局（G表示Guojia国家，C表示Cehui测绘，J表示Ju局）制订的地理信息系统的坐标系统。它是一种对经纬度数据的加密算法，即加入随机的偏差。国内出版的各种地图系统（包括电子形式），必须至少采用GCJ-02对地理位置进行首次加密。

## 3.程序思路

在具体操作前，首先需要注册高德地图开发者账号，然后申请Web服务API密钥（Key）。

### 3.1获取行政区的shp文件

1.  构造高德Web API的行政区查询请求URL，例如：[http://restapi.amap.com/v3/config/district?key=<用户的key>&keywords=<关键词>&subdistrict=<子级行政区级别(0或1)>&extensions=all](http://restapi.amap.com/v3/config/district?key=<用户的key>&keywords=<关键词>&subdistrict=<子级行政区级别(0或1)>&extensions=all)。须注意的一点是：extensions参数应为all，若为base则只返回基本信息，其中不包含坐标串。

2.  将获取到的坐标串，从GCJ-02坐标系转换为WGS-84坐标系。

3.  利用第三方库pyshp，将返回的坐标串写入对应的shp文件。

### 3.2获取aoi的shp文件

1. 构造高德Web API的POI搜索请求URL，搜索POI有四种方式，分别是：关键词搜索、周边搜索、多边形搜索和ID查询。这里我们使用关键词搜索的方式，指定`city`并设置`citylimit`为`true`，只搜索城市内的数据。例如：[https://restapi.amap.com/v3/place/text?keywords=北京大学&city=beijing&output=xml&offset=20&page=1&key=<用户的key>&extensions=all](https://restapi.amap.com/v3/place/text?keywords=北京大学&city=beijing&output=xml&offset=20&page=1&key=<用户的key>&extensions=all)。

2. 拿到POI的id后，请求[https://www.amap.com/detail/get/detail?id=<POI的id>](https://www.amap.com/detail/get/detail?id=<POI的id>)。

3. 若返回的数据包含边界坐标则写入对应shp文件，若返回的数据不包含边界坐标则将其父poi的id和name加入循环列表。

## 4.第三方依赖

- requests

- configparser

- [pyshp](https://github.com/GeospatialPython/pyshp)

  

## 5.注意事项

- result/district_shp文件夹中，分别包含有中国各省份、湖北各城市、武汉行政区的个人地理数据库。result/aoi_shp文件夹中，分别包含有武汉市高等教育院校、武汉市公园、武汉市景点的个人地理数据库。这些数据是在ArcMap中构建的数据库，一并上传，供需要的读者下载使用。
- cookies参数，在getPoiShp.py文件中的getRawData函数中指定在headers参数中。config.ini文件中cookies参数配置，因为cookies中的=和；对ini文件的读取造成了困扰，以后有机会完善。
- 每一个shp文件写入成功后，在控制台会输出提示，注意查看。
- 若想研究pyshp的用法，推荐查阅pyshp的github页面，其作者的文档很详细。笔者额外加了写入.prj文件的代码。

## 6.Contact Me

 如果有什么建议，欢迎联系我 [zixinwan@foxmail.com](mailto:zixinwan@foxmail.com) 或提issue。欢迎star! 
