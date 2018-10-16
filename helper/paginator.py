from django.core.paginator import Paginator
from django.conf import settings

def getPages(request, objectlist):
    """ 分页器 """
    # 获取GET方法请求的参数，得到当前的页码。若获取失败则默认为1
    currentPage = request.GET.get('page', 1)

    # 每7个对象为一页，参数可写于 setting.py 里面
    paginator = Paginator(objectlist, settings.EACHPAGE_NUMBER)
    objectlist = paginator.page(currentPage)
 
    return paginator, objectlist
