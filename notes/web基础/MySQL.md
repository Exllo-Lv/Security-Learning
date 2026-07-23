# MySQL基础

数据库是实体,能合理保管数据,目前使用关系型数据库管理系统(RDBMS)来存储和管理大数据量

关系型数据库:MySQL(3306),MsSQL(1433),Oracle(1521)

非关系型数据库:MongoDB,Redis(6379)

**MySQL**是最流行的关系型数据库管理系统

## **本地部署配置以及MySQL数据库操作**

![image-20260711162334556](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260711162334556.png)

`show database`查看数据库 `use database_name;`使用数据库 `show tables`查看数据库的表

![image-20260711162530520](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260711162530520.png)

`select [字段] from [表名] ` `show [字段] from [表名]`

![image-20260711163144691](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260711163144691.png)

### 相关函数

|         函数         |     描述     |
| :------------------: | :----------: |
|        user()        | 查看当前用户 |
|      version()       |  数据库版本  |
|      database()      |   数据库名   |
| @@version_compile_os |   操作系统   |
|      @@basedir       | 查看安装目录 |
|      @@datadir       | 查看数据目录 |

`creat database [数据库名]` 创建数据库 `drop database [数据库名]` 删除数据库

![image-20260711163711945](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260711163711945.png)

`create table [表名] (字段 类型 约束[字段 类型 约束]);`

字段类型

| 数据类型 |  描述  |
| :------: | :----: |
| VARCHAR  | 字符串 |
|   TEXT   | 大文本 |
|  ＩＮＴ  | 整数值 |
|  FLOAT   | 浮点数 |

|      约束      |       描述       |
| :------------: | :--------------: |
| auto_increment |     自动增长     |
|    not null    |     不能为空     |
|  primary key   |       主键       |
|     unique     | 表示该属性的值是 |
|    default     |      默认值      |



### 数据库增删改查

#### 增加数据

```sql
insert into table_name(字段名) VALUES (值1,值,2);
insert into users(user_id,uer,user_title),values(1,'admin','MyTest');
```

数据是字符型,必须用单双引号,如"value"

```sql
insert into users values(值1,值2);
insert into users values(1,'admin','MySQL');
```

一次插入多个值

```sql
insert into users(user_id,user,user_tittle) value(1,'admin','MySQL'),(2,'admiN@123','MsSQL');
```

#### 查看数据

MySQL数据库,使用SQL SELECT数据

```sql
select 字段 from 表名
select * from users;
```

limit限制[索引] [条数]

```sql
select * from users limit 0,1;
```

<img src="https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716110800695.png" alt="image-20260716110800695" style="zoom:50%;" />

<img src="https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260716111006315.png" alt="image-20260716111006315" style="zoom:67%;" />

依照字段查询信息

```sql
select * from users where id =1;
```

#### 修改数据

```sql
UPDATE 表名 SET　字段名１＝值１，值２．．．　[where 条件];
```

删除数据

```sql
DELETE FROM 表名 WHERE [条件];
delete from users; 
truncate users;
```

逻辑运算符

```sql
select * from users where user = 'admin' and city ='beijing'
```

or

```sql
select * from users where user = 'admin' and city ='beijing'
```

or 和 and 连用

```sql
select * from users where user = 'admin' adn ctiy ='beijing' or city='shanghai'
```



#### 其他操作

过滤重复值 distinct 

```sql
select distinct user from users;
```

查询表中以S开头的数据

```sql
select * from where user like "%s";
```

对查询结果排序*

```sql
select 字段1,字段2,...from 表名 order by 字段名 [asc || desc ];#asc表示升序,dESC表示降序,默认为升序
```

分组查询*

```sql
select 字段1,字段2,...from 表名 group by 字段1,... [having 条件表达式];
```

`group by`按照字段或者多个字段分组*

```sql
select * from users group by city;
```

子查询*

先执行括号中语句,最后执行最外层语句

```sql
select * from users where user_id > (select user_id from users where user='admin12');
```

联合查询* 查询的字段必须前后一致

```sql
select version() union select user();
```

