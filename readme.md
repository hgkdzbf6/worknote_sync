欢迎使用日志同步工具

使用方法：修改以下配置文件

```json
{
    "remote_path": "ssh://your_name@your_ip_address:your_port/your_path/",
    "Windows_base_path": "your_Windows_path",
    "wsl_base_path": "your_wsl_path",
    "macOS_base_path": "your_macOS_path"
}
```

将他重命名为config.json，即可使用。

使用方法：

执行`python3 run.py -d`下载数据，也就是相当于pull
执行`python3 run.py -u`上传数据，也就是相当于push

