# Docker学习



## 什么是docker

开源的容器引擎,能完整打包应用和其依赖包,然后发布到Linux或者Windows操作系统的机器上,完全沙箱机制,之间不会有任何接口



## 使用的场景

模拟开发环境,若使用虚拟机体积臃肿占用内存高,程序性能受影响;Docker在运行中与虚拟机类似,均为虚拟化技术,但不会模拟底层硬件.



## 学习使用部署练习过程

使用Ubuntu拉取docker

![image-20260708194820438](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260708194820438.png)

`service docker status` 查看docker服务的运行环境

![image-20260708195003756](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260708195003756.png)

`docker search` 查找镜像 `docker pull 'ID'`拉取镜像 `docker images` 查看本地镜像

![image-20260709191902476](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709191902476.png)

`docker run ID`运行容器 `docker ps -a` 查看运行的容器 `docekr stop` `docker kill` `dockerstart` `docker rm`强制启动关闭删除容器

![image-20260709192412231](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709192412231.png)

`docker exec -it ID /bin/bash` 进入容器 

![image-20260709192703619](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709192703619.png)

## Docker-Compose 

Compose是用于定义和运行多容器docker应用程序的工具,通过Compose,可以使用YML文件来配置应用程序所需要的服务然后使用命令

![image-20260709193215069](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709193215069.png)

docker compose 版本

![image-20260709193251608](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709193251608.png)

`docker compose version`管理多容器应用



## Docker-Compose 挂代理

`sudo mkdir p /etc/systemd/system/docker.service.d` 创建配置目录

`sudo vim /etc/systemd/system/docker.service.d/http-proxy.conf`创建或编辑配置文件

写入代理

```
[Service]
Environment="HTTP_PROXY=
Environment="HTTPS_PROXY=
Environment="NO_PROXY=localhost,127.0.0.1,docker-registry.example.com,.corp"
```

![image-20260709193825244](https://exllo-lv-github-notes-picture-1452130078.cos.ap-nanjing.myqcloud.com/img/image-20260709193825244.png)
