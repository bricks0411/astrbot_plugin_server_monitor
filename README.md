# astrbot_plugin_server_monitor
<p align="center">
  <img src="https://count.getloli.com/@ServerMonitor?name=ServerMonitor&theme=asoul&padding=10&offset=0&align=top&scale=1&pixelated=1&darkmode=auto" alt="Moe Counter">
</p>
<p align="center">
✨making dev work easier✨
</p>


<p align="center">
  <img src="https://img.shields.io/badge/License-AGPL_3.0-blue.svg" alt="License: AGPL-3.0">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/AstrBot-v4.5.7+-orange.svg" alt="AstrBot v4.9.0+">
</p>

一个用于 **AstrBot** 的服务器监控插件，用于定时记录宿主机状态、实时查询服务器信息，并提供历史趋势图展示。

以 Windows、Linux 等系统为基础开发与测试，使插件具有跨平台兼容性。

该插件主要用于 **轻量级服务器监控** 场景，使用简单（仅需安装一个运行依赖），且可以直接在聊天中查询服务器基本运行状态，无需额外部署完整监控系统，降低各位开发者的维护难度。

## 提醒

🚨 需要提前安装 `matplotlib` 库，否则插件将无法正常运行

  ```
  pip install matplotlib
  ```

🚨 在 `docker` 环境下获取的内核数据可能不准确，请酌情对待

## 项目架构

插件采用 **分层解耦** 的设计思路，整体分为 5 个核心模块 / 层级，职责单一且依赖关系清晰：

1. **入口层**：仅保留 `main.py` 作为插件对外入口，负责命令注册和事件处理；
2. **核心层**：是插件的业务核心，`models.py` 定义系统指标 / 主机信息的数据模型，`monitor.py` 封装数据采集、查询等核心服务接口；
3. **适配层**：基于 `base.py` 抽象接口，分别实现 `linux.py`/`windows.py` 两套系统的数据采集逻辑，保证跨系统适配能力；
4. **工具层**：`chart.py` 为核心层提供数据可视化能力（折线图 / 状态卡片）；
5. **数据库层**：`db.py` 负责监控数据的持久化存储和历史查询，支撑核心层的数据需求。

入口模块调用核心层服务，核心层依赖适配层完成跨系统数据采集，同时调用工具层做可视化、数据库层做数据存储，各层间仅依赖抽象接口，无强耦合。

<img width="2794" height="1759" alt="image-20260305180058038" src="https://github.com/user-attachments/assets/abcdc992-a0a3-429c-843a-8377b6eaaf50" />

## 项目结构

```text
astrbot_plugin_server_monitor/
├── core/                 # 核心监控逻辑
│   ├── __init__.py
│   ├── monitor.py
│   └── models.py
├── adapters/             # 系统适配层
│   ├── __init__.py
│   ├── base.py
│   ├── windows.py
│   ├── linux.py
│   └── factory.py
├── font/                 # 字体资源
│   └── LXGWWenKai-Regular.ttf
├── utils/                # 工具模块
│   ├── __init__.py
│   └── chart.py          # 图表绘制
├── database/             # 数据存储
│   ├── __init__.py
│   └── db.py
├── config.py             # 插件配置
├── _conf_schema.json     # 配置结构定义
├── __init__.py
├── README.md
├── LICENSE
└── main.py               # 插件入口
```

## 功能

### 1. 定时监控服务器指标

**介绍**

插件会按一定的时间间隔（目前定为 $30$ 秒，后续配置文件更新后，支持自行设置）采集服务器指标并保存，包括：

- CPU 使用率
- 内存使用率
- 磁盘使用率
- 系统负载（仅 Linux 支持）

该任务会在插件加载时自动开始，无需手动设定。采集到的数据将会写入本地数据库，用于后续趋势分析。

### 2. 实时状态查询

**介绍**

当用户发送查询指令时，插件会 **立即获取当前服务器状态** 并生成状态卡片。

该数据 **仅用于即时展示，不会写入数据库**。

展示内容包括：

- CPU 使用率
- 内存使用率
- 磁盘使用率
- 系统 Load
- 主机信息（Hostname / OS / Architecture）

并以 **图形化卡片** 的形式输出。

**用法**

在群聊 or 私聊中发送：

```
/查询状态
```

示例如下：

<img width="875" height="401" alt="image-20260305173435608" src="https://github.com/user-attachments/assets/e92c2d38-8e8a-4aec-b695-52a2b02fdc68" />

### 3. 历史趋势图

**介绍**

插件支持查询最近一段时间内的服务器运行趋势。

目前支持：

- 最近 **1 小时** 数据趋势
- CPU / 内存 / 磁盘 / Load 折线图

用于快速观察服务器负载变化。

**用法**

在群聊 or 私聊中发送

```
/查询历史
```

示例如下：

<img width="876" height="315" alt="image-20260305173724555" src="https://github.com/user-attachments/assets/5147bc3b-766e-497b-b069-d82e6114e7ab" />

## 运行环境

- Python 3.10 +

- AstrBot (4.9.0 +)

- matplotlib

- psutil

- sqlite

## 安装

将插件放入 AstrBot 插件目录：

```
AstrBot/data/plugins/
```

目录结构示例：

```
AstrBot/
└── data/
    └── plugins/
        └── astrbot_plugin_server_monitor/
```

随后重启 AstrBot 或热加载，即可启用插件。

## 字体

插件默认使用字体：

```
LXGW WenKai
```

用于保证中文渲染效果。

字体文件位于：

```
font/LXGWWenKai-Regular.ttf
```

## License

本项目基于 **GNU General Public License v3.0** 开源。

你可以：

- 自由使用
- 修改源码
- 再发布

但必须遵守 GPL 协议条款，并保持开源。

详细内容见：`LICENSE`

## TODO

-  指标异常告警
   -  在异步任务中添加数据检测逻辑，一旦发现错误，则向管理员 QQ 推送消息
   -  设置提醒步长，防止频繁告警造成打扰

-  可配置监控阈值
   -  通过 WebUI 进行监控阈值的可配置化

-  更灵活的历史查询范围
   -  通过 WebUI 进行历史查询范围的选择

-  更丰富的监控指标
-  图表样式优化

## 贡献

- Star 这个项目（感谢支持，给点⭐人磕一个✋😭🤚）；
- 提交 issue 报告问题
- 提出新功能建议
- 提交 pull request 改进代码
