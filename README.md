[![](https://img.shields.io/travis/padeny/tastypie_api.svg?style=flat-square)](https://travis-ci.org/padeny/tastypie_api)
[![Coverage Status](https://coveralls.io/repos/github/padeny/tastypie_api/badge.svg?branch=master)](https://coveralls.io/github/padeny/tastypie_api?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Tastypie Api
=====

对[Tastypie](https://github.com/django-tastypie/django-tastypie)框架做了一些封装


#### 重定义 Response 格式

>
接口响应字段说明

status_code: 自定义的响应状态码, 0 表示请求被成功处理 1 表示请求未被成功处理  其他如 401未登录 405 请求方法不支持...

msg: 提示信息

meta: 字典, 对于List接口, 包含一些元数据, 如数据量分页信息等

data: 字段或者数组, 响应的具体数据

- GET  [/api/v1/entries/2/]
    ```
        {
            "status_code": 0,
            "msg": "SUCCESS",
            "meta": {},
            "data": {
                "created": "2012-05-01T22:05:12",
                "image": null,
                "slug": "first-post",
                "title": "First Post!",
                "user": null
            }
        }
    ```

- GET  [/api/v1/entries/?limit=20]
    ```
        {
            "status_code": 0,
            "msg": "SUCCESS",
            "meta": {
                "limit": 20,
                "next": null,
                "page_num": 1,
                "previous": null,
                "total_count": 5
            },
            "data": [
                {
                    "created": "2012-05-01T22:05:12",
                    "image": null,
                    "slug": "first-post",
                    "title": "First Post!",
                    "user": null
                },
                ...
            ]
        }
    ```

  - Unauthenticated  [/api/v1/entries/?limit=20]

    ```
        {
            "status_code": 401,
            "msg": "未认证",
            "meta": {},
            "data": {}
        }
    ```

>
在需要自定义接口response 时可调用tastypie_api 已封装好的  http.Result或者 http.FailedResult, 两者均是 HttpResponse
的子类, 如下实例接口中可根据需要调用

```python
    ...

    def clear_adopters(self, request, **kwargs):
            """
            """
            self.is_authenticated(request)
            self.method_check(request, allowed=['patch'])
            user = request.user
            deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
            deserialized = self.alter_deserialized_list_data(request, deserialized)
            try:
                profile_id = deserialized['profile_id']
            except KeyError:
                raise DataFormatError(msg="data format error!")
            try:
                profile = self.Meta.queryset.get(id=profile_id)
            except ObjectDoesNotExist:
                return FailedResult(msg='not found')
            if profile.owner != user:
                return FailedResult(msg='the profile not belongs to current user')
            profile.adopters.clear()
            return Result(msg="success")

```

#### 集成 `multipart/form-data` FileUpload

- POST

 tastypie 默认不支持`multipart/form-data`方式创建 model 的 类FileField字段, 关于这个问题gitlab 上有相关的讨论
 [issue](https://github.com/django-tastypie/django-tastypie/issues/1419),另已有开发者提了 PR, 但一直未被合并, 这里将其集成进来了

- PATCH or PUT

 支持以 from-data 的方式更新单个资源, 默认会报错
`django.http.request.RawPostDataException: You cannot access body after reading from request's data stream`

原因参考 (https://github.com/django-tastypie/django-tastypie/issues/42#issuecomment-6071991)

 对于PATCH or PUT方法做了如下处理:

```python
    def convert_post_to_patch(request):
        request.body
        request._read_started = False
        return convert_post_to_VERB(request, verb='PATCH')


    def convert_post_to_put(request):
        request.body
        request._read_started = False
        return convert_post_to_VERB(request, verb='PUT')
```

#### 增加`page_num`分页参数

tastypie 默认返回的 meta 字段有
```
    {
        "limit": 20,
        "next": null,
        "offset": 0,
        "previous": null,
        "total_count": 5
    }
```
`limit`: 每页的数据条数

`offset`: 当前页第一条数据的位置

`next`: 下一页的 uri

`previous`: 上一页的 uri

`total_count`: 接口返回的数据总数


常见的两种分页方式:

- 上滑加载更多

    这种方式可根据接口返回数据中的 meta 中的`next`直接获取

- 显示页码列表

    这种情况下总的页数 可以根据 total_count/limit 计算得到; 但如果访问指定页时, 每次都需要重新计算 `offset=(page_num - 1) * limit`

因此, 覆写了 tastypie 的 paginator 中部分方法, 以 `page_num` 代替 `offset`, 表示当前页的页码;
如查询第二页
`/api/v1/entries/?limit=2&page_num=2`

```
    {
        "status_code": 0,
        "msg": "SUCCESS",
        "meta": {
            "limit": 2,
            "next": "/api/v1/entries/?limit=2&page_num=3",
            "page_num": 2,
            "previous": "/api/v1/entries/?limit=2&page_num=1",
            "total_count": 5
        },
        "data": [
            {
                "created": "2012-05-01T22:05:12",
                "image": null,
                "slug": "third-post",
                "title": "Third Post!",
                "user": null
            },
            {
                "created": "2012-05-01T22:05:12",
                "image": null,
                "slug": "forth-post",
                "title": "Forth Post!",
                "user": null
            }
        ]
    }
```

#### 自定义 url is_authentication 和method_check 装饰器

自定义 url, 需要在各自的方法中分别调用is_authentication和method_check进行登录认证和请求方法检查

```python
    def check_name(self, request, **kwargs):
        # 每个自定义url的方法需要手动调用该方法
        self.is_authenticated(request)
        self.method_check(request, allowed=['get'])
        profile_name = request.GET.get("profile_name", "").strip()
        user = request.user

        if self.Meta.queryset.filter(profile_name=profile_name, owner=user).exists():
            data = {"is_existed": "true"}
        else:
            data = {"is_existed": "false"}
        return Result(data=data)
```

(https://github.com/django-tastypie/django-tastypie/pull/1321), 借鉴它的思路, 实现认证装饰器custome_api, allowed为接口接受的请求方法, login_required可选,指接口是否需要登录,默认为 True

```python
    @custom_api(allowed=["get"], login_required=True)
    def check_name(self, request, **kwargs):
        profile_name = request.GET.get("profile_name", "").strip()
        user = request.user

        if self.Meta.queryset.filter(profile_name=profile_name, owner=user).exists():
            data = {"is_existed": "true"}
        else:
            data = {"is_existed": "false"}
        return Result(data=data)
```

## TODO
补充Qucik Start
