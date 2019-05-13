import re

# 引用分组,精确获取多个标签内的内容
# "\1"是对第一个分组的引用,同理......

str = "<span><h1><a>hello world!</a></h1></span>"
pattern = r"<(.+)><(.+)><(.+)>.*</\2></\1>"
result = re.match(pattern, str)
print(result.groups())

# 执行如下图:
