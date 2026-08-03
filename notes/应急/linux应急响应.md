# Linux应急响应



## 入侵排查思路

### 一.账号安全

一般攻击拿下一台主机 , 想要留个后门 , 通常会新建一个管理员账号

1、用户信息文件 : cat /etc/passwd

```
root:x:0:0:root:/root:/bin/bash
用户名:密码占位符:uid:gid:用户描述:用户家目录:分配的shell终端
uid=0 root
uid=1-499 系统用户
uid=500-999 服务用户
uid=1000 -》 x 普通用户


account:password:UID:GID:GECOS:directory:shell

用户名：密码：用户ID：组ID：用户说明：家目录：登陆之后shell
```

2、shadow文件 : cat /etc/shadow

```
root:$6$oGs1PqhL2p3ZetrE$X7o7bzoouHQVSEmSgsYN5UD4.kMHx6qgbTqwNVC5oOAouXvcjQSt.Ft7ql1WpkopY0UV9ajBwUt1DpYxTCVvI/:16809:0:99999:7:::

用户名：加密密码：密码最后一次修改日期：两次密码的修改时间间隔：密码有效期：密码修改到期到的警告天数：密码过期之后的宽限天数：账号失效时间：保留
```



命令:

- `w`    在线用户数,每个人登录多久,空闲时间,负载
- `who`  在线用户,终端,登陆时间   输出字段中: ttyX:本地显示器登录  pts/X :SSH,Xshell,图形终端远程登录
- `uptime` 查看登录多久多少用户负载



植入后门用户命令

```
useradd -p `openssl passwd -1 -salt 'salt' 123admiN` TomcatU -o -u 0 -g root -G root -s /bin/bash -d /home/Tomcat
```

- `useradd` 添加用户
- `-p openssl passwd -1 -salt 'salt' 123admiN`设置用户密码
  - `openssl passwd` openssl生成linux密码哈希
  - `-1` 使用Md5加密算法
  - `salt 'salt'` 固定盐值为salt
- `TomactU`用户名
- `-u 0` 指定uid为0 **即超级管理员root权限**
- `-o` 允许重复uid
- `-g root` 指定初始主组
- `-G root` 指定附加附属组也加入root
- `-s /bin/bash` 登录shell设为bash,这个账号可以ssh,本地交互式终端,如果是`/sbin/nologin`则禁止登录
- `-d /home/Tomcat` 指定用户家目录



### 二.入侵排查

1. 查询特权用户(uid = 0)

   `awk -F: '$3==0' /etc/passwd`

2. 查询可以远程登录的账号信息

   `awk '/$1|$6/{print $1}' /etc/shadow`

3. 除root帐号外，其他帐号是否存在`sudo`权限。如非管理需要，普通帐号应删除sudo权限

   `more /etc/sudoers | grep -v "#|$" | grep "ALL=(ALL)"`

4. 禁用删除多余可疑账号

   ```
   usermod -L user   禁用帐号，帐号无法登录，/etc/shadow第二栏为!开头
   userdel user          删除user用户
   userdel -r user      将删除user用户，并且将/home目录下的user目录一并删除
   ```

   

### 三.历史命令

通过bash_history查看账号执行过的系统命令

1. root的历史命令

   ```
   cat /root/.bash_history
   
   # bash反弹shell  
   # ssh链接
   # apt/yum install 
   # vim
   # crontab
   # 网站敏感文件
   ```

2. 打开/home各帐号目录下的`.bash_history`，查看普通帐号的历史命令

   为历史的命令增加登录的IP地址、执行命令时间等信息：

   1. 保存1万条命令 , 默认历史命令只保留1000条

      `sed -i 's/^HISTSIZE=1000/HISTSIZE=10000/g' /etc/profile`

   2. 在/etc/profile的文件尾部添加如下行数配置信息：

   ```
   vim /etc/profile
   
   ######jiagu history xianshi#########
   USER_IP=`who -u am i 2>/dev/null | awk '{print $NF}' | sed -e 's/[()]//g'`
   if [ "$USER_IP" = "" ]
   then
   USER_IP=`hostname`
   fi
   export HISTTIMEFORMAT="%F %T $USER_IP `whoami` "
   shopt -s histappend
   export PROMPT_COMMAND="history -a"
   ######### jiagu history xianshi ##########
   ```

   3. source /etc/profile 让配置生效

3. 把历史命令导入到记事本中分析

   `cat .bash_history >> history.txt`

   痕迹清理

   ```
   历史操作命令的清除：history -c
   	但此命令并不会清除保存在文件中的记录，因此需要手动删除.bash_profile文件中的记录。
   ```

   

### 四.查看外联

使用`netstat`网络连接命令，分析可疑端口、IP、PID

netstat -antlp | more                  more是可以分页查看

查看下pid所对应的进程文件路径 , 如果是木马文件 直接 rm -rf 木马

ls -l /proc/PID/exe 或file/proc/PID/exe   （$PID 为对应的pid 号)





### 五.查看进程

ps分析进程

```
top
ps aux | grep pid
kill -9 $pid
```





### 六.开机启动项

| 运行级别 | 含义                                                      |
| -------- | --------------------------------------------------------- |
| 0        | 关机                                                      |
| 1        | 单用户模式，可以想象为windows的安全模式，主要用于系统修复 |
| 2        | 不完全的命令行模式，不含NFS服务                           |
| 3        | 完全的命令行模式，就是标准字符界面 ( 用的多 )             |
| 4        | 系统保留                                                  |
| 5        | 图形模式 ( 用的多 )                                       |
| 6        | 重启动                                                    |

Init 切换运行级别

init 5

查看运行级别命令 

runlevel

查看开机启动配置文件

```
more /etc/rc.d/rc[0~6].d          *[0~6]是指运行级别
more /etc/rc.d/rc5.d
```

例子 : 当我们需要开机启动运行自己的脚本时，只需要将可执行脚本丢在/etc/init.d目录下

然后在/etc/rc.d/rc*.d中建立软链接即可

ln -s /etc/init.d/木马 /etc/rc.d/rc5.d/S木马         ( 没有运行 )ln -s /etc/init.d/sshd /etc/rc.d/rc3.d/S100ssh

此处sshd是具体服务的脚本文件，S100ssh是其软链接，**S开头代表加载时自启动**；如果是**K开头的脚本文件**不启动。



### 七.定时任务

利用crontab创建计划任务

```
crontab -l    列出某个用户cron服务的详细内容
提示：默认编写的crontab文件会保存在 (/var/spool/cron/用户名 例如: /var/spool/cron/root)

crontab -r    删除每个用户cront任务(谨慎：删除所有的计划任务)
crontab -e    使用编辑器编辑当前的crontab文件
cat /etc/crontab  #*

如：1 * * * * echo "hello world" >> /tmp/test.txt 每分钟写入文件
        分 时 日 月 周
```



计划任务中重点关注的目录

```
/var/spool/cron/* 
/etc/crontab
/etc/cron.d/*
/etc/cron.daily/* 
/etc/cron.hourly/* 
/etc/cron.monthly/*
/etc/cron.weekly/
/etc/anacrontab
/var/spool/anacron/*
```



### 八.查看系统日志

日志默认存放位置：/var/log/

查看日志配置情况：more /etc/rsyslog.conf

| 日志文件          | 说明                                                         |
| ----------------- | ------------------------------------------------------------ |
| /var/log/cron     | 记录了系统定时任务相关的日志                                 |
| /var/log/cups     | 记录打印信息的日志                                           |
| /var/log/dmesg    | 记录了系统在开机时内核自检的信息，也可以使用dmesg命令直接查看内核自检信息 |
| /var/log/mailog   | 记录邮件信息                                                 |
| /var/log/messages | 记录系统重要信息的日志。这个日志文件中会记录Linux系统的绝大多数重要信息，如果系统出现问题时，首先要检查的就应该是这个日志文件 |
| /var/log/btmp     | **记录错误登录日志**，这个文件是二进制文件，不能直接vi查看，而要使用lastb命令查看 |
| /var/log/lastlog  | 记录系统中所有用户最后一次登录时间的日志，这个文件是二进制文件，不能直接vi，而要使用 lastlog 命令查看 |
| /var/log/wtmp     | 永久记录所有用户的登录、注销信息，同时记录系统的启动、重启、关机事件。同样这个文件也是一个二进制文件，不能直接vi，而需要使用 last 命令来查看 |
| /var/log/utmp     | 记录当前已经登录的用户信息，这个文件会随着用户的登录和注销不断变化，只记录当前登录用户的信息。同样这个文件不能直接vi，而要使用w,who,users等命令来查询 |
| /var/log/secure   | **记录验证和授权方面的信息，只要涉及账号和密码的程序都会记录，比如SSH登录**，su切换用户，sudo授权，甚至添加用户和修改用户密码都会记录在这个日志文件中 |

日志分析技巧：

```
统计登录失败的记录，确认服务器是否遭受暴力破解
grep -o "Failed password" /var/log/secure|uniq -c
grep -o "Failed" /var/log/secure|uniq -c

输出登录爆破的第一行和最后一行，确认爆破时间范围
grep "Failed" /var/log/secure|head -1
grep "Failed" /var/log/secure|tail -1
grep "Failed" /var/log/secure | grep 45.82.137.151

定位有哪些IP在爆破：
grep "Failed password for root" /var/log/secure|grep -E -o "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"|uniq -c

爆破用户名字典是什么？
grep "Failed password" /var/log/secure|perl -e 'while($_=<>){ /for(.*?) from/; print "$1\n";}'|uniq -c|sort -nr

2、登录成功的IP有哪些：    
grep "Accepted" /var/log/secure | awk '{print $11}' | sort | uniq -c | sort -nr | more

登录成功的日期、用户名、IP：
grep "Accepted" /var/log/secure | awk '{print $1,$2,$3,$9,$11}' 

3、增加用户日志
查看命令 : grep "useradd" /var/log/secure 
   - Jul 10 00:12:15 localhost useradd[2382]: new group: name=kali, GID=1001
   - Jul 10 00:12:15 localhost useradd[2382]: new user: name=kali, UID=1001, 			-	- GID=1001,home=/home/kali,shell=/bin/bash
   - Jul 10 00:12:58 localhost passwd: pam_unix(passwd:chauthtok): password changed for kali
   

4、删除用户日志
查看命令: grep "userdel" /var/log/secure
   - Jul 10 00:14:17 localhost userdel[2393]: delete user 'kali'
   - Jul 10 00:14:17 localhost userdel[2393]: removed group 'kali' owned by 'kali'
   - Jul 10 00:14:17 localhost userdel[2393]: removed shadow group 'kali' owned by 'kali'
```

关于SSH暴力破解的处置方法

```
1、禁止向公网开放管理端口，若必须开放应限定管理IP地址并加强口令安全审计（口令长度不低于8位，由数字、大小写字母、特殊字符等至少两种以上组合构成）。
2、更改服务器ssh默认端口. nmap -sV 
3、部署入侵检测设备，增强安全防护。
```



### 九.Web日志

```
centos
apache2
/var/log/apache2

/var/log/httpd    access.log error.log
nginx
var/log/nginx/    access.log error.log  
宝塔
/var/wwwlogs/
也有可能在软件安装目录下log目录下
```

Web访问日志记录了Web服务器接收处理请求及运行时错误等各种原始信息。通过对WEB日志进行的安全分析，不仅可以帮助我们定位攻击者，还可以帮助我们还原攻击路径，找到网站存在的安全漏洞并进行修复。

Web日志安全分析时的思路和常用的一些技巧。

```
1、列出当天访问次数最多的IP命令：
cut -d- -f 1 log_file|uniq -c | sort -rn | head -20
2、查看当天有多少个IP访问：
awk '{print $1}' log_file|sort|uniq|wc -l
3、查看某一个页面被访问的次数：
grep "/index.php" log_file | wc -l
4、查看每一个IP访问了多少个页面：
awk '{++S[$1]} END {for (a in S) print a,S[a]}' log_file
5、将每个IP访问的页面数进行从小到大排序：
awk '{++S[$1]} END {for (a in S) print S[a],a}' log_file | sort -n
6、查看某一个IP访问了哪些页面：
grep ^111.111.111.111 log_file| awk '{print $1,$7}'
7、去掉搜索引擎统计当天的页面：
awk '{print $12,$1}' log_file | grep ^\"Mozilla | awk '{print $2}' |sort | uniq | wc -l
8、查看2018年6月21日14时这一个小时内有多少IP访问:
awk '{print $4,$1}' log_file | grep 21/Jun/2018:14 | awk '{print $2}'| sort | uniq | wc -l
```



## 工具

Rootkit 查杀

Rootkit是一种特殊的恶意软件，它的功能是在安装目标上隐藏自身及指定的文件、进程和网络链接等信息，比较多见到的是 Rootkit 一般配合木马、后门等其他恶意程序结合使用。

### chkrootkit

第一步 : 安装编译工具包

yum install gcc gcc-c++ make glibc-static -y

第二步 : 下载安装包

网址：[http://www.chkrootkit.org](http://www.chkrootkit.org/)

```plain
使用方法：
tar zxvf chkrootkit.tar.gz 
cd chkrootkit-0.55
make sense             #编译完成没有报错的话执行检查
./chkrootkit             # 运行程序开始检测
```

安装方法二：http://www.linuxfly.org/post/138/ 

带有`**INFECTED ( 感染 )**`, 是被病毒感染的文件 , 这个时候你就要进行系统排查了

假如说 ps 被感染了 , 修复的方法就是 , 重新下载一个ps文件 , 然后替换到你的受害主机中 

### rkhunter

网址：[http://rkhunter.sourceforge.net](http://rkhunter.sourceforge.net/)

使用方法：

```plain
wget https://nchc.dl.sourceforge.net/project/rkhunter/rkhunter/1.4.4/rkhunter-1.4.4.tar.gz --no-check-certificate
如果命令不能下载你就去官网下载 , 然后copy到linux主机中
tar -zxvf rkhunter-1.4.4.tar.gz
cd rkhunter-1.4.4
./installer.sh --install
rkhunter -c
```



### 河马webshell查杀

linux版：

河马webshell查杀：[http://www.shellpub.com](http://www.shellpub.com/)

深信服Webshell网站后门检测工具：http://edr.sangfor.com.cn/backdoor_detection.html

使用方法

```plain
1. 下载64位版本
wget -O /opt/hm-linux.tgz http://dl.shellpub.com/hm/latest/hm-linux-amd64.tgz?version=1.8.2
2. 解压缩
cd /opt/
tar xvf hm-linux.tgz   
chmod +x hm
```

注意:

不要将本软件放置到web目录下

不要在web目录下运行软件

```plain
3. 查看帮助
./hm -h
4.  查看版本
./hm version
5. 扫描后门
 ./hm scan 你的web目录
```
