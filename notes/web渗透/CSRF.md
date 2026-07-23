# CSRF 跨站请求伪造



## 漏洞描述

CSRF是针对网站的恶意利用

CSRF是攻击者通过伪造用户浏览器的请求,欺骗浏览器去访问一个自己已经登录认证过的网站,执行一些操作例如修改密码,发邮件,购买商品,财产操作等.由于曾经认证过,所以浏览器会以为是用户的操作而执行

即攻击者盗用了你的身份向第三方网站发起恶意请求

![image-20260716115324393](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716115324393.png)

![image-20260716145137335](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716145137335.png)

> [!IMPORTANT]
>
> **攻击过程**
>
> 1. 用户c打开了浏览器,登陆了信任网站A
>
> 2. 用户信息通过验证后,A向C发送了cookie信息
>
> 3. 用户在未退出A网站的情况下,访问了B网站发来的恶意URL
>
> 4. B接收到用户C访问请求后,B将包含恶意访问A的代码返回给用户C的浏览器,浏览器自动访问A网站并携带用户C的cookie执行B的恶意请求
>
>    网站A根据请求的Cookie处理,最终执行恶意操作请求的为用户C

## 检测漏洞

1. 一般在用户密码修改,信息修改,添加账号,发布文章等一些敏感操作位置,如果没有二次校验(验证码,密码等)就可以进行测试
2. 检测工具有: CSRFTester,CSRF Requeset Builder, BurpSuite



### 靶场检测

**测试过程:** 点击修改->抓包点击提交->制作poc->修改提交内容->访问poc

![image-20260716143351917](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716143351917.png)

![image-20260716144514650](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716144514650.png)

这里复制到登陆过的浏览器后直接成功了





## CSRF 与 XSS 组合拳

Discuz论坛

![image-20260716151444775](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716151444775.png)

在管理员点击备份数据的时候抓包

<img src="https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716161857209.png" alt="image-20260716161857209" style="zoom:67%;" />

```
/discuz_x1.5_sc_utf8/upload/uc_server/admin.php?m=db&a=operate&t=export&appid=0&backupdir=backup_260716_kGKUIj
```

构建URL链接

```
http://127.0.0.1/discuz_x1.5_sc_utf8/upload/uc_server/admin.php?m=db&a=operate&t=export&appid=0&backupdir=aaaa%26backupfilename%3Daaaa
```

把这个链接发在发表图片的位置

![image-20260716162826243](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716162826243.png)

管理员访问后,就可直接看到数据库

![image-20260716165922009](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716165922009.png)

## 防御措施

1. 对关键操作增加**token**参数,token值必须随机
   - 嵌入表单隐藏字段,或者自定义HTTP请求头
2. 对**Referer**进行验证
3. 关于安全的会话管理(避免会话被利用)
   - 不要在客户端保存敏感信息,比如身份认证信息
   - 测试直接关闭,退出时会话过期机制
   - 设置会话过期机制,比如15分钟内无操作,则登录自动超时
4. 访问控制安全管理
   - 敏感信息的修改时需要对身份进行二次认证,
   - 使用post
   - 通过http头部的referer来限制原页面,增加验证码,一般用在登录,也可以用在其他重要信息
5. 双重提交Cookie
   - 先服务器下发(set-cookie)
   - 前端读取整个Cookie
   - 发起非GET请求时会将读的Cookie放入自定义请求头中
   - 服务器收到请求后会提取cookie和请求头中的自定义请求头对比





## CSRF绕过

### 针对WAF规则

这类技术核心是混淆攻击载荷，让WAF的规则匹配失效，但目标服务器或浏览器依然能正常解析。

- **编码与特殊字符混淆**：
  - 利用多种编码（如URL编码、Unicode编码）或插入换行符(`\n`)、制表符(`\t`)等，把关键字符“藏”起来。例如，用`%0A`（换行符）替换空格，或用大写`HREF`绕过只检测小写的WAF。一个真实案例是在`<a`标签的标签名和属性间插入换行符，即`<a\nHREF="/logout">`，成功绕过WAF。
- **大小写与注释干扰**：
  - 混合使用大小写来绕过关键词匹配，或在攻击语句中插入无害的注释（如SQL的`--`、HTML的`<!-- -->`），干扰WAF对完整攻击特征的识别。
- **HTTP参数污染 (HPP)**：
  - 通过重复提交同一个参数（如 `id=1&id=2`）。WAF和后台程序对这种情况的处理方式可能不同（如WAF取第一个，程序取最后一个），攻击者可以利用这种**解析差异**绕过检测。
- **协议层面的变异**：
  - 修改HTTP请求的细节，如改变`GET`/`POST`的大小写（`gEt`），或调整HTTP头的顺序，这些都可能绕过依赖固定格式的WAF规则。



### 针对特定CSRF防御措施的绕过

当WAF配合应用程序的CSRF防御逻辑时，攻击目标会更明确。

- **绕过基于`Referer`的防御**：如果应用只检查`Referer`头存在性，攻击者可通过`<meta name="referrer" content="never">`让浏览器不发送该头。若应用只检查`Referer`是否包含其域名，攻击者可把合法域名作为子域名或参数放入自己的恶意链接中。
- **绕过基于`Content-Type`的防御**：利用WAF和应用对`Content-Type`解析的不一致。例如，WAF不检测`application/json`，但应用又能解析，攻击者便可发送JSON格式的恶意载荷。另一个例子是使用大小写变体`Application/x-www-form-urlencoded`，或直接**不发送`Content-Type`头**，都可能绕过检查。
- **直接攻击CSRF Token机制**：最简单的思路是**直接删除Token参数或其值**；或尝试**用其他随机值替换**，看服务器是否只做简单的存在性检查。如果Token可预测或有效期很长，攻击者也可能通过**提前获取一个合法Token**来构造请求。