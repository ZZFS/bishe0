import re

text='Tom is 6 yeard old Mike is 34 yesrs old Jack is 7877 years old'

pattern =re.compile(r'\d+')

print(pattern.findall(text))

pattern=re.compile(r'[A-Z]\w+')
print(pattern.findall(text))
