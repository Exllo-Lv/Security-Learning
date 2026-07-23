# SSRF 服务端请求伪造

是一种由攻击者构造请求,由服务器端发起请求的安全漏洞,一般情况下SSRF的目标是从外网无法访问的内部系统

![image-20260716190510850](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716190510850.png)



## 漏洞原理

SSRF形成的原因大都是由于服务端提供了从其他服务器获取数据的功能而又没有对目标服务器目标地址做过滤和限制,用户对目标地址可控,比如从用户指定的URL地址获取文本内容,加载指定地址的图片,下载等



## 漏洞分类

- 显示对攻击者的响应
  - 它显示对攻击者的响应，因此在服务器获取攻击者要求请求的URL后，他将会把响应发送回攻击者。返
    回结果到客户端。会返回这个网址的界面或对应的HTML代码
- 不显示响应
  - 和上面正好相反，不会返回结果到客户端。当您从未从初次请求中获取有关目标服务的任何信息时，就会发生这种ssrf。通常，攻击者将提供url，但是该url中的数据将永远不会返回给攻击者。要在这种情况下确认漏洞，攻击者必须使用Burp，DNSLOG等类似工具。这些工具可以通过强制服务器向攻击者控制的服务器发出DNS或HTTP请求来确认服务器是易受攻击的。这种ssrf通常易于验证，但难以利用



## 漏洞函数

**PHP**中可能存在SSRF漏洞的函数 `file_get_content()` `fsockopen()` `curl_exec()`

- `file_get_content` :将整个文件或一个URL指向的文件,以字符串性质展示给用户,读取文件,URL,本地协议内容,默认支持`http://` `https://` `file://` `php://` `dict://`
- `file_put_content`: 将字符串写入文件,若路径可控,可写木马

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>
提交
 ̪<title>
    
  </head>
 
      <body>
        <form action="./file_get_contents.php" method="GET" style="text-al
ign:center;">
          <p>Submit URL</p>
 
          <p><input type="text" name="url" width="400px"></p>
 
          <input type="submit" name="submit">
        </form>
 
      </body>
 
</html>
```

```php
<?php
            if(isset($_GET['url'])) # isset判断有没有提交url           
            {
            $content=file_get_contents($_GET['url']);# 这一行$content变量将远程URL内容保存到content中
            $filename='./images/'.rand().'.jpg';\ # ⽣成⼀个文件路径            				file_put_contents($filename,$content); # 获取远程的内容后写道新的文件中      
            echo $_GET['url']; #输出url
            $img="<img src=\"".$filename."\"/>";#将保存到文件名保存到标签中
            }
echo @img;
?>
```



- `curl_exec()`:对远程的url发起请求,并将请求的结果返回前端页面
  - 是是 SSRF 漏洞里**利用能力最强**的函数，gopher 协议是核心攻击手段
  - 不受 `allow_url_fopen` 限制，即使关闭该配置依然能发起远程请求

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>
提交
</title>
 
</head>
 
<body>
<form action="./curl_exec.php" method="GET" style="textalign:center;">
<p>Submit URL ̪</p>
 
<p><input type="text" name="url" width="400px"> </p>
 
<input type="submit" name="submit">
</form>
 
</body>
 
</html>
```

```php
<?php>
//
利⽤⽅式很多最常⻅的是通过file、dict、gopher这三个协议来进⾏渗透，接下来也主要是集中curl()函数的利⽤⽅式
function curl($url){
$ch = curl_init(); /*初始化curl连接句柄*/
curl_setopt($ch, CURLOPT_URL, $url); /*设置连接URL*/
curl_setopt($ch, CURLOPT_HEADER, 0); /*不输出头⽂件的信息*/
curl_exec($ch);   /*执⾏获取结果*/
curl_close($ch);  /*关闭curl连接句柄*/
}
$url = @$_GET['url'];
curl($url);
?>
```



- `fsockopen():`使用该函数实现获取用户制定的URL数据;该函数会使用socket跟服务器建立TCP连接,传输原始数据,属于底层网络函数

```php
<?php
$host=$_GET['url'];
$fp = fsockopen("$host", 80, $errno, $errstr, 30);
if (!$fp) {
echo "$errstr ($errno)<br />\n";
} else {
$out = "GET / HTTP/1.1\r\n";
$out .= "Host: $host\r\n";
$out .= "Connection: Close\r\n\r\n";
fwrite($fp, $out);
while (!feof($fp)) {
echo fgets($fp, 128);
}
fclose($fp);
}
?>
```

| 函数               | 渗透测试场景                          | 正常开发业务场景             | 优缺点                             |
| ------------------ | ------------------------------------- | ---------------------------- | ---------------------------------- |
| curl_exec()        | SSRF全流程利用,读文件,Redis/MySQL提权 | 爬虫,第三方接口,API,http请求 | 功能最全,攻击风险最高              |
| file_get_content() | 简单读本地文件,基础网页探测           | 快速读文本/接口返回          | 代码简洁,但高阶协议失效,受配置限制 |
| fsockopen()        | 批量端口发包,底层自定义,TCP发包       | 底层Socket通信,SMTP发邮件    | 底层可控,但利用复杂,无协议封装     |



## 攻击方式

主要攻击方式如下:

1. 对外网服务器所在的内网/本机进行主机扫描、端口扫描、服务探测。
2. 攻击运行在内网或本地的应⽤程序
3. 攻击内外网的web应⽤，主要是使⽤ get 参数就可以实现的攻击（⽐如struts2， sqli、thinkphp 等）;
4. 用File协议读取服务器⽂件。
5. 各个协议调⽤探针： http,file,dict,ftp,gopher 等 



### 各协议利用

SSRF支持很多协议所以漏洞利用户的方式也有挺多的。 

- http://通过http协议访问内⽹主机web服务，或发送Get数据包
- file://  本地⽂件传输协议，主要⽤于访问本地计算机中的⽂件 
- dict://字典服务器协议，dict是基于查询相应的TCP协议
- gopher://互联⽹上使⽤的分布型的⽂件搜集获取⽹络协议，出现在http协议之前
- sftp:// SSH⽂件传输协议，或安全⽂件传输协议
- ldap://轻量级⽬录访问协议。它是IP⽹络上的⼀种⽤于管理和访问分布式⽬录信息服务的应⽤程序协议
- tftp://基于lockstep机制的⽂件传输协议，允许客户端从远程主机获取⽂件或将⽂件上传⾄远程主机





#### HTTP协议

进行内网端口探测-通过返回的时间和长度判断端口是否开放/与web站点访问

`http://127.0.0.1/pikachu-master/vul/ssrf/ssrf_curl.php?url=http://www.baidu.com`探测是否连通外网

- 限制1:URL需要URL编码
- 限制2:服务器防火墙,白名单拦截

![image-20260716201253000](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716201253000.png)

`http://127.0.0.1/pikachu-master/vul/ssrf/ssrf_curl.php?url=http://127.0.0.1:3306`探测内网端口

![image-20260716201213178](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716201213178.png)



#### file协议

伪协议,读取敏感的文件信息

- linux 的⽹站⽬录 /var/www/html/  

- /var/logs/httpd/access.log error.log  
- /var/logs/Nginx/access.log error.log  
- file:///var/logs/httpd/access.log  
- file:///etc/passwd Linux ⽤户基本配置信息  
- file:///c:/windows/win.ini windows 系统基本配置信息  
- file:///etc/shadow Linux⽤户密码等敏感信息（⼀般需要root⽤户才能查看 web服务⽤户⼀般没有权 限查看）



#### dict 协议

内网服务探测(dict伪协议)

字典服务器协议,通常用于让客户端使用过程中能够访问更多的字典源,但是在如果可以使用dict协议那么就可以获取取⽬标服务器端口上运行的服务版本等信息

- dict:// ....:3306 MySQL ,ssh,redis,sqlserver等(通过响应时间判断端口开放)

#### Gopher协议

Gopher协议 是比HTTP协议更早出现的协议，现在已经不常使⽤了，但是在SSRF漏洞中可以利⽤ gopher协议发送各种格式的请求包，这样便可以解决漏洞点不在GET参数的问题。所有WEB服务器都支持gopher协议。 

- 协议格式: gopher://<host / TCP数据流>

> [!CAUTION]
>
> 由于Gopher协议的特殊格式，在SSRF利⽤Gopher攻击⽬标时，需要对数据包进⾏两次URL编码。
>
> 1. 第⼀次URL将URL中的特殊字符进行转义，以便于传输和解析。
> 2. 第二次是为了让Gopher能正常解析,因为gopher使用的ASCII,需要将URL的所有字符转换为ASCII码的可打印字符,才能被Gopher协议正确解析

