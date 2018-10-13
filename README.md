[![coverage report](http://gitlab.mathartsys.com/Paden/mas_tastypie_api/badges/master/coverage.svg)](http://gitlab.mathartsys.com/Paden/mas_tastypie_api/commits/master)
[![pipeline status](http://gitlab.mathartsys.com/Paden/mas_tastypie_api/badges/master/pipeline.svg)](http://gitlab.mathartsys.com/Paden/mas_tastypie_api/commits/master)
![](https://img.shields.io/badge/python-3.6-brightgreen.svg)


Mas Tastypie Api Framework
=====

对[Tastypie](https://github.com/django-tastypie/django-tastypie)框架做了一些封装, 内部使用

## 封装
 - 重定义 Response 格式
 - 集成 `multipart/form-data` FileUpload
 `https://github.com/django-tastypie/django-tastypie/issues/1419`
 - 增加`page_num`分页参数
 
## Tips
 - 前后端分离Django csrftoken的获取
 > 内网项目可直接关闭 csrf 验证

 参考[stackoverflow](https://stackoverflow.com/questions/15388694/does-sessionauthentication-work-in-tastypie-for-http-post)
