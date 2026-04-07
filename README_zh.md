## Live Resonance

[English](README.md) | **中文**

使用任意 MIDI 设备实时演奏《星痕共鸣》游戏中的虚拟乐器。

### 功能

Live Resonance 从 MIDI 设备获取 MIDI 输入，并将相应的键盘事件播放到系统。它旨在帮助用户使用 MIDI 设备实时演奏游戏内的虚拟乐器，突破使用电脑键盘的局限性。

核心功能：

- 实时 MIDI 输入消息监听和键盘事件输出。
- 高度可配置的 MIDI 到键盘映射及冲突解决算法。
- 内置《星痕共鸣》虚拟乐器预设。
- 支持按通道、音高和力度进行输入过滤。
- MIDI 输出重定向到其他 MIDI 设备。

### 安装方法

1. 从 [Releases](https://github.com/esun-z/live-resonance/releases) 页面下载最新版本。
2. 将下载的压缩包解压到所需位置。
3. 以管理员身份运行 `LiveResonance.exe` 启动应用程序。

### 许可证

本项目采用 GNU General Public License v3.0 许可证。详见 [LICENSE](LICENSE) 文件。

禁止将本项目打包为闭源软件进行销售。如发现盗卖，请向平台举报。

### 待办事项

- [x] 添加预设以将符合 General MIDI 标准的鼓组信号映射到游戏内鼓组。
- [ ] 吉他和贝斯映射的更多控制键支持。
- [ ] 本地化。

### 开发

本项目使用 Astral uv 进行依赖管理。请先[安装 Astral uv](https://docs.astral.sh/uv/getting-started/installation/)。

1. 克隆仓库：

    ```bash
    git clone https://github.com/esun-z/live-resonance.git
    cd live-resonance
    ```

2. 安装依赖：

    ```bash
    uv sync
    ```

3. 编译 UI 表单：
    ```bash
    uv run scripts/ui_compile.py
    ```

4. 运行应用程序：

    ```bash
    uv run main.py
    ```

### 贡献

欢迎贡献代码！如有任何改进或错误修复，请提交 issue 或 pull request。