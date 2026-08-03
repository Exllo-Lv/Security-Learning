# Win应急响应

**应急响应流程(PDCERF)**

1. **P（Preparation，准备）**：准备阶段，组建应急响应团队，准备工具和文档

2. **D（Detection，检测）**：检测阶段，确认安全事件是否发生，收集初步信息

3. **C（Containment，抑制）**：抑制阶段，限制事件影响范围，防止进一步扩散

4. **E（Eradication，根除）**：根除阶段，清除恶意代码、后门，修复漏洞

5. **R（Recovery，恢复）**：恢复阶段，恢复系统正常运行，验证业务完整性

6. **F（Follow-up，跟踪）**：跟踪阶段，总结复盘，输出报告，加固防御





## 文件分析



### 开机启动文件

 一般情况下，各种木马病毒等恶意程序，都会在计算机开启的过程中自动在Windows 系统中可以通过以下三种方式查看开机启动项。

 利用操作系统中的启动菜单栏

 `C:\Users\alone\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`  ![image-20260721110058768](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260721110058768.png)

任务管理器

![image-20260721110154571](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260721110154571.png)

注册表

`regedit`



```
计算机\HKEY_LDCAL_MACHLNE\SOFTHARE\Microsoft\Windows\CurrentVersion\Run 

计算机\HKEY_CURRENT_USER\SOFTHARE\Microsoft\Windows\CurrentVersion\Run 这个两个都可以添加开机启动文件  
```

 其中在注册表中新建启动文件，在msconfig中是可以看到的，但那时在启动文件夹中 不显示的。  

 利用组策略设置自动开启  

`gpedi.msc`![img](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709277037737-9b5d89e9-8537-4048-9963-fb4704f4127f.png)



### Temp临时异常文件

 temp（临时文件夹），`C:\Users\Administrator\AppData\Local\Temp`内。很多临时文件 会放到这里；用于收藏文件、浏览网页时的临时文件，编辑文件等，  

Win+r :`%temp%`即可打开该文件夹  

![image-20260721111245188](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260721111245188.png)

> [!NOTE]
>
> 查看temp文件夹有没有pe文件（ exe，dll，sys，msi ）或者是具有特别大的tmp文件   

 fscan msscan frp  

 PE文件指的是Windows系统中可以执行的文件，不仅仅是有exe文件  

 tmp特殊性  

1. temp问文件夹位于ramdisk上，与通常的磁盘文件系统相比，这使写入操作和文件操作快
   很多。

1. temp文件夹对当前登录用户具有读写访问权限，即完全控制权限
   所以恶意程序在传播的时候向temp文件夹是一定可以写入的。

 可以文件在线查杀  

 https: [www.virustotal.com/](http://www.virustotal.com/) 国外网站

 https: [www.virscan.org/](http://www.virscan.org/) 国内网站  



### 浏览器信息分析

 在被黑客拿下的服务器，很有可能会使用浏览器进行网站的访问，因此我们可以查看 浏览器记录，探索浏览器是否被使用下载恶意代码，浏览器浏览痕迹查看，黑客可能 浏览了某些页面。  

 IE浏览器 工具 --> 浏览器栏 --> 历史记录和下载的内容。  

 实际上服务器是用来提供服务的，所以你打开浏览器会有一个安全提示，浏览器文件 下载记录查看，黑客很有可能通过浏览器下载一些自己恶意文件  



### 文件时间属性分析

在Windows系统下，文件属性得时间属性行具有：创建时间、修改时间、访问时间 （默认情况下是禁用）  

 默认情况下，计算机是以修改时间作为展示的

> [!IMPORTANT]
>
> 重点排查:
>
> web目录  开机自启目录   临时文件目录  

通过everything语法排查



### 最近打开文件分析

Windows系统中默认记录系统中最近打开使用得文件信息。 可以在目录

C:\Users\Administrator\Recent下查看，也可以使用win+r打开运行输入:  

 `%UserProfile%\Recent`  

查看，然后利用Windows中得筛选条件查看 具体得时间范围得文件  



## 网络进程分析

### 可疑进程发现与关闭

计算机与外部网络通信是简历在TCP或UDP协议上的，并且每一次通信都具有不同得 端口（0-65535）,如果计算机被种木马后，肯定会与外部网络通信，那么此时就可通 过网络连接状态，找到对应得进程ID，然后关闭进程ID。  

`netstat -ano`

 `netstat -ano | find "ESTABLISHED"` # 查看网络建立连接状态

 `tasklist /svc | find "3224"` # 查看具体PID进程对应程序 

`taskkill /PID` pid值 /T /F 关于TCP连接状态介绍 # 强制关闭进程及其开启得子进程  

![image-20260721145210191](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260721145210191.png)

**LISTENING**:表示处于监听状态，就是说该端口是开放的，等待连接，但是还没有被连接。 

**ESTABLISHED**：表示已经建立连接，表明两台机器正在通信。 

**FIN_WAIT_1**: 表示服务器端主动请求关闭TCP连接，并且主动发送FIN之后，等待客户端恢复 ACK得状态。

**FIN_WAIT_2**: 表示客户都安主动请求关闭TCP连接，并且主动发送FIN之后，等待服务端恢复 ACK得状态。 

**TIME_WAIT** : 表示结束了本次连接，说明曾经访问过，现在访问结束了。 

**CLOSING** : 等待远程TCP对连接中断得确认。 

**CLOSED** : 没有任何连接状态。  



## 系统分析

### windows计划任务

 在计算机中可以通过设定计划任务，在固定时间执行固定得操作，一般情况下，恶意代码也可能在固定得时间设置执行。  

`schtasks`查找计划任务

或 开始-->任务计划程序

### 隐藏账号发现与删除

net user 查找登录和未登录的用户

注册表中可以看到隐藏用户

`lusrmgr.msc`查看本地用户和组

**超级隐藏用户**

还有一种更加隐藏得方式是通过注册表添加用户，注册表相当于一个数据库，保存着系统相关得信息，这样新建的隐藏用户在本地用户和组中是不显示的

```
HKEY_LOCAL_MAICHINE\SAM\SAM\Domains\account\user\names\test$ 
```

\#默认打不开需要修改权限

在此处查找我们刚刚添加的用户test$ 

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709288831738-829d5762-35e8-48cd-94a9-ea8cd00693a8.png)

 将项Test![img](https://cdn.nlark.com/yuque/__latex/b72a7ab987927e962a9fca271b83bd80.svg)(000003ec)项的F值，然后对000003ec导出。  

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709288859790-516d0e33-6452-4689-9bca-ceb24a561651.png)

删除test$账号 

net user test$ /del  

 把000003ec.reg、test.reg导入到注册表中  

 在注册表窗口内把HKEY_LOCAL_MACHINE\SAM\SAM键权限改回原来的样子  

 至此隐藏超级账号就创建好了,实际上的原理就是通过注册表新建账号,绕过本地用户和组记录账号信息,但是我测试的不同两台机器同时，登陆管理员账号会让另一个下线,所以不如直接新建添加到管理员,然后从注册表导出,删除账号,再导入注册表,ok  

所以说要查账号**直接去注册编辑表**中去查，其他都不准都会有问题



### 补丁查看和更新

 Windows系统支持补丁修补漏洞，可以使用systeminfo查看系统信息，并展示对应得 系统补丁信息编号，也可以在卸载软件中查看系统补丁和第三方补丁。  

在Windows10中在控制面板->程序->程序和功能->查看已安装的更新





## 网站Webshell查杀

D盾_防火墙专为IIS设计的一个主动防御的保护软件, 以内外保护的方式, 防止网站和 服务器给入侵, 在正常运行各类网站的情况下,越少的功能, 服务器越安全的理念而设 计! 限制了常见的入侵方法, 让服务器更安全  

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709289237423-7c887a45-b642-40ad-bcc1-14740c9c53f9.png)

 查杀到目录后直接右键打开文件得位置，删除木马再次查杀直到无木马，除了asp 🐎，php得木马D盾也可以查杀，功能很强大还能查看克隆账号等。  

关于网站日志，采用360星图分析工具，进行分析



## Webshell分析工具

星图分析工具  

 配置与使用  

1. 打开/conf/config.ini在log_file:这一行填写日志路径，可以是目录或具体文件。
   比如log_file:D:\weblog\1.log

1. 运行start.bat自动处理日志

1. 结果会生成在result目录

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709551071659-48179576-3d14-4716-a61b-0cda7a4547f5.png)

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709551077313-9d870bb9-362b-4102-a6e5-316dfb49058f.png)



## Windows日志分析

### 系统日志

系统日志包含Windows系统组件记录得事件，例如：在启动过程中加载驱动程序或其 他系统组件失败将记录在系统日志中，系统组件所记录得事件类型由Windows预先确定。

 默认位置  

 `c:\windows\system32\winevt\Logs\System.evtx`  

`eventvwr.msc`事件查看器

![image-20260721153531557](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260721153531557.png)

#### **系统日志筛选**

工具自带了筛选功能，不同类型的日志具有不同编号，每一种操作都有不同的日志ID

选中右键属性 , 查看关于安全日志登录部分的事件 ID 和登录类型代码的含义见下面2个表。

**事件ID**

| EventID(2000/XP/2003) | EventID(2000/XP/2003) | 描述                                          | 日志名称 |
| --------------------- | --------------------- | --------------------------------------------- | -------- |
| 528                   | 4624                  | 成功登录                                      | Security |
| 529                   | 4625                  | 失败登录                                      | Security |
| 680                   | 4776                  | 成功/失败的账户认证                           | Security |
| 624                   | 4720                  | 创建用户                                      | Security |
| 636                   | 4732                  | 添加用户到启用安全性的本地组中                | Security |
| 632                   | 4728                  | 添加用户到启用安全性的全局组中                | Security |
| 2934                  | 7030                  | 服务创建错误                                  | system   |
| 2944                  | 7040                  | IPSEC服务服务的启动类型已从禁用更改为自动启动 | system   |
| 2949                  | 7045                  | 服务创建                                      |          |

**登录类型ID**

成功/失败登录事件提供的有用信息之一是用户/进程尝试登录（登录类型），但Windows 将此信息显示为数字，下面是数字和对应的说明：

| 登录类型 | 登录类型                | 描述                                                         |
| -------- | ----------------------- | ------------------------------------------------------------ |
| 1        | Interactive             | 所谓交互式登录就是指用户在计算机的控制台 上进行的登录，也就是在本地键盘上进行的登 录。 场景：本地电脑登录、PSEXEC、KVM登录 |
| 2        | Network                 | 用户或计算机从网络登录到本机，如果网络共 享，或使用 net use 访问网络共享，net view 查 看网络共享 场景：IPC、WMIC、WinRM |
| 3        | Batch                   | 批处理登录类型，无需用户干预                                 |
| 4        | Service                 | 在Windows系统中，每种服务都被配置在某个 特定的用户账户下运行，当一个服务开始时， Windows首先为这个特定的用户创建一个登录 会话，这将被记为类型5。 |
| 5        | Unlock                  | 你可能希望当一个用户离开他的计算机时相应 的工作站自动开始一个密码保护的屏保，当一 个用户回来解锁时，Windows就把这种解锁操 作认为是一个类型7的登录，失败的类型7登录 表明有人输入了错误的密码或者有人在尝试解 锁计算机。 |
| 6        | NetworkCleartext        | 这种登录表明这是一个像类型3一样的网络登 录，但是这种登录的密码在网络上是通过明文 传输的，WindowsServer服务是不允许通过明文 验证连接到共享文件夹或打印机的，据我所知 只有当从一个使用Advapi的ASP脚本登录或者 一个用户使用基本验证方式登录IIS才会是这种 登录类型。“登录过程”栏都将列出Advapi |
| 7        | NewCredentials          | 进程或线程克隆了其当前令牌，但为出站连接 指定了新凭据        |
| 8        | Remotelnteractive       | 使用终端服务或远程桌面连接登录                               |
| 9        | Cachedlnteractive       | 用户使用本地存储在计算机上的凭据登录到计 算机（域控制器可能无法验证凭据），如主机 不能连接域控，以前使用域账户登录过这台主 机，再登录就会产生这样日志 |
| 10       | CachedRemotelnteractive | 与 Remotelnteractive 相同，内部用于审计目的                  |
| 11       | CachedUnlock            | CachedUnlock                                                 |

### 应用程序日志

 包含由应用程序或系统程序记录得事件，主要记录程序运行方面事件，例如：数据库 程序可以在应用程序日志记录文件错误，程序开发人员可以自行监视那些事件。  

 `C:\windows\system32\winevt\Logs\Applocation.evtx` 



### 安全日志

记录系统得安全审计事件，包含各类得登录日志，对象访问日志、进程追踪日志、特 权使用、账号管理、策略变更、系统事件。安全日志也是调查取证中最常用到得日 志。

 默认 

 `c:\windows\system32\winevt\Logs\Security.evtx`  



### 日志分析工具

将日志拷贝下来，离线分析。

![null](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/1709270340861-b5740a54-06ba-411a-8b71-552e9b67512b.png)

#### Log Parser

Log Parser（是微软公司出品的日志分析工具，它功能强大，使用简单，可以分析基于文本的日志文件、XML 文件、CSV（逗号分隔符）文件，以及操作系统的事件日志、注册表、文件系统、ActiveDirectory。它可以像使用 SQL 语句一样查询分析这些数据，甚至可以把分析结果以各种图表的形式展现出来。

https://www.microsoft.com/en-us/download/details.aspx?id=24659

基本查询语法

```
`Logparser.exe –i:EVT –o:DATAGRID "SELECT * FROM c:\xx.evtx"`
```

查询登录成功的事件

```
`LogParser.exe -i:EVT –o:DATAGRID "SELECT * FROM Security.evtx where EventID=4624"`
```

指定登录时间范围的事件

```
`LogParser.exe -i:EVT –o:DATAGRID "SELECT * FROM Security.evtx where TimeGenerated>'2018-06-19 23:32:11' and TimeGenerated < '2023-08-22 23:34:00' and EventID=4624"`
```

提取登录成功的用户名和IP

```
LogParser.exe -i:EVT –o:DATAGRID "SELECT EXTRACT_TOKEN(Message,13,' ') as EventType,TimeGenerated as LoginTime,EXTRACT_TOKEN(Strings,5,'|') as Username,EXTRACT_TOKEN(Message,38,' ') as Loginip FROM Security.evtx where EventID=4624" 
```

查询登录失败的事件

```
LogParser.exe -i:EVT –o:DATAGRID "SELECT * FROM Security.evtx where EventID=4625"
```





## 应急响应工具**

病毒分析：

 PCHunter：http://www.xuetr.com/

火绒剑： https://www.onlinedown.net/soft/10053617.htm

Process Explorer：https://learn.microsoft.com/zh-cn/zhcn/sysinternals/downloads/process-explorer

processhacker：https://processhacker.sourceforge.io/downloads.php

autoruns：https://learn.microsoft.com/zh-cn/enus/sysinternals/downloads/autoruns 

OTL：https://www.bleepingcomputer.com/download/otl/

病毒查杀：

卡巴斯基：http://devbuilds.kasperskylabs.com/devbuilds/KVRT/latest/full/KVRT.exe 

（推荐理由：绿色版、最新病毒库） 

大蜘蛛：https://free.drweb.ru/download+cureit+free 

（推荐理由：扫描快、一次下载只能用1周，更新病毒库） 

火绒安全软件：https://www.huorong.cn/

360杀毒：http://sd.360.cn/download_center.html

 病毒动态：  

CVERC-国家计算机病毒应急处理中心：  https://www.cverc.org.cn/

微步在线威胁情报社区：  https://x.threatbook.com/

火绒安全论坛：  https://bbs.huorong.cn/forum-59-1.html

爱毒霸社区：  https://www.ijinshan.com/keep.html

腾讯电脑管家：  https://support.qq.com/product/415334

 在线病毒扫描网站：  

https://www.virscan.org/  //多引擎在线病毒扫描网 v1.02，当前支持 41 款杀毒引擎 

https://habo.qq.com/	//腾讯哈勃分析系统

https://virusscan.jotti.org/	// Jotti恶意软件扫描系统  

http://www.scanvir.com/		//针对计算机病毒、手机病毒、可疑文件等进行检测分析 

 WebShell查杀

D盾_Web查杀：   http://www.d99net.net/index.asp

河马webshell查杀：http://www.shellpub.com/

深信服Webshell网站后门检测工具：   http://edr.sangfor.com.cn/backdoor_detection.html

 Safe3：http://www.uusec.com/webshell.zip\  



## 入侵排查思路 分析方法**

- 收集信息：收集与系统安全相关的信息，包括日志文件、进程列表、网络连接、系统配置、 Webshell查杀、Web日志等。
- 分析信息：对收集到的信息进行分析，确定异常行为和潜在威胁。
- 确认威胁：确认系统存在威胁，并确定其类型和程度。
- 阻止攻击：采取相应的措施，尽快阻止攻击并减少损失。
- 恢复系统：对受到攻击的系统进行恢复，确保其正常运行。 



- 系统账号 
- 异常端口 , 进程 , 外连 网络连接 
- 启动项 , 计划任务 , 服务 
- 注册表 , 组策略 
- 系统相关信息 , 如 补丁 
- 日志分析 
- 自动查杀