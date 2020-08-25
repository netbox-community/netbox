# Gunicorn

如同大多数 Django 应用程序一样, NetBox 在 HTTP 服务器后方，运行为一个 [WSGI 应用](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) . 本文档表述了如何以 [gunicorn](http://gunicorn.org/) 的方式进行安装和配置, 当然，其他 WSGIs 也是可行的，并且应该能以类似的方式工作.

## 配置

NetBox 为 gunicorn 提供了一个默认配置文件. 只需要复制 `/opt/netbox/contrib/gunicorn.py` 为 `/opt/netbox/gunicorn.py` 即可使用. (我们复制文件后使用，而不是直接指向它，以确保对它的任何更改不会因将来的升级而丢失。)

```no-highlight
# cd /opt/netbox
# cp contrib/gunicorn.py /opt/netbox/gunicorn.py
```

缺省配置文件已经适合大多数情况的初始化要求, 如果您希望修改配置文件中的服务绑定的 IP 地址和端口, 或者希望进行性能调整, 请参考 [Gunicorn 文档](https://docs.gunicorn.org/en/stable/configure.html) 查阅可用的配置参数.

## systemd 安装 

我们使用 systemd 控制 gunicorn 和 NetBox 的后台工作进程. 首先, 复制 `contrib/netbox.service` 和 `contrib/netbox-rq.service` 到 `/etc/systemd/system/` 目录，并重载 systemd 守护进程:

```no-highlight
# cp contrib/*.service /etc/systemd/system/
# systemctl daemon-reload
```

然后, 启动 `netbox` 和 `netbox-rq` 服务，并允许它们在操作系统启动时自动装载:

```no-highlight
# systemctl start netbox netbox-rq
# systemctl enable netbox netbox-rq
```

您可以通过 `systemctl status netbox` 验证 WSGI 服务是否正在运行:

```no-highlight
# systemctl status netbox.service
● netbox.service - NetBox WSGI Service
   Loaded: loaded (/etc/systemd/system/netbox.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2019-12-12 19:23:40 UTC; 25s ago
     Docs: https://netbox.readthedocs.io/en/stable/
 Main PID: 11993 (gunicorn)
    Tasks: 6 (limit: 2362)
   CGroup: /system.slice/netbox.service
           ├─11993 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12015 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12016 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
...
```

当您确认 WSGI 进程已经启动并成功运行, 下一步进行 HTTP 服务器配置.
