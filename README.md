# 亚马逊产品关键词研究

独立保存 Amazon-Skills 的 amazon-keyword-research 模块，包含中文网页操作面板、Python 采集服务，以及原始 AI 研究流程说明与 Bash 脚本。

## 来源与授权

- 原作者：Nexscope AI
- 上游：https://github.com/nexscope-ai/Amazon-Skills
- 原始模块：https://github.com/nexscope-ai/Amazon-Skills/tree/2bcb8cb019cfac6a1e420b11f86209df5ea47686/amazon-keyword-research
- 复制版本：`2bcb8cb019cfac6a1e420b11f86209df5ea47686`
- 许可证：MIT，原始版权声明完整保存在 LICENSE。
- SKILL.md、_meta.json、scripts/research.sh 按该版本原样保留；本 README 为新增中文说明。

## 中文操作面板（推荐）

### 第一次启动

1. 安装 Python 3.10 或以上版本（Windows 安装时勾选 Add Python to PATH）。无需第三方 Python 依赖、卖家账号或 API 密钥。
2. 在本仓库点击 **Code → Download ZIP**，解压到电脑。
3. Windows 双击 `start.bat`；macOS / Linux 在解压目录打开终端，运行 `python3 app.py`。
4. 保持启动窗口打开，在浏览器访问 **http://127.0.0.1:8765**。
5. 输入英文或目标站点语言的产品核心词，选择站点，点击“开始采集”。可直接点击生辰石项链、悬臂伞示例填词。
6. 采集完成后可筛选、复制关键词，或导出 CSV 用 Excel 打开。CSV 包含 UTF-8 BOM，并处理以公式符号开头的单元格。

关闭终端或按 Ctrl+C 停止服务。端口被占用时，macOS / Linux 可用 `PORT=8766 python3 app.py`；Windows 命令提示符先执行 `set PORT=8766`，再执行 `py -3 app.py`。浏览器地址也改用对应端口。

### 面板功能

- 12 个站点；基础采集 4 次查询，a–z 扩展 30 次查询。
- 实时进度、全局不区分大小写去重、发现来源追踪。
- 关键词包含筛选，复制或导出当前筛选结果。
- 单次请求 8 秒超时，请求间隔 0.4 秒；明确显示失败查询及部分结果，不自动绕过站点限制。
- 服务仅绑定本机，校验 Host / Origin，不开放给外网。单进程一次只运行一个采集任务。
- 不写入采集结果文件；最多保留 20 个任务在内存中。刷新页面会丢失当前页面任务视图，重启服务清空所有任务。请及时导出。

**这是本地运行版本，GitHub 仓库页面不能直接采集，也不是已部署的在线网站。** 不建议直接改成公开监听地址；公开部署需要另加身份验证和配额。

## 文件

| 文件 | 用途 |
| --- | --- |
| app.py | Python 本地服务及联想词采集 |
| web/index.html | 中文操作面板 |
| start.bat | Windows 启动入口 |
| tests/test_app.py | 采集逻辑和本地接口测试 |
| SKILL.md | 原作者给 AI 助手的研究流程 |
| scripts/research.sh | 获取亚马逊搜索联想词 |
| _meta.json | 原模块元数据 |
| LICENSE | 原作者 MIT 许可证 |

## 原始 Bash 脚本使用

需要 Bash、Python 3、curl 和 sort。Windows 可使用已配置这些工具的 WSL 或 Git Bash。在下载后的仓库目录运行：

```bash
# 美国站生辰石项链
bash scripts/research.sh "birthstone necklace" us

# 澳洲站户外伞
bash scripts/research.sh "cantilever umbrella" au

# 保存终端输出
bash scripts/research.sh "birthstone necklace" us > keywords.txt
```

支持的站点配置：us、uk、de、fr、it、es、jp、ca、au、in、mx、br。配置存在不代表所有站点均已验证可用。

脚本查询原词及 best、cheap、top 前缀，再查询核心词加 a–z 后缀的组合，单站点单次约 30 次请求。结果数量取决于接口和核心词，不保证获得 100–200 个词。

输出包含标题和分区，并非 CSV；导入 Excel 需要整理。原脚本仅在前缀组和字母组内分别去重，两组之间仍可能重复。

## 能力边界

- 搜索联想词不含精确月搜索量、销量、广告竞价或完整 ASIN 流量词反查。
- 竞品、季节趋势和机会评分是 AI 另外研究的步骤，不是脚本直接返回的数据。
- Google 趋势不等于亚马逊站内搜索量，相关词也不代表有转化。
- 原始 Bash 脚本保留原样；中文面板独立使用 Python 采集，加入超时、失败提示和请求间隔。
- 美国站 `birthstone necklace` 单次真实接口查询成功，返回 10 条联想词；其余站点未逐一实测。接口可用性会受网络和亚马逊限制影响。
- 已通过 4 项自动测试（去重与来源、部分失败、全部失败、本地接口及外部 Origin 限制），并检查 Python / 前端 JavaScript 语法。未完成真实浏览器交互验收。
- 没有安装为 AI 技能，也不会自动优化或提交广告。

运营时建议结合自己的广告搜索词报表，保留来源、站点和采集日期，再按相关性、点击、订单和花费筛选。


## 开发验证

```bash
python3 -m unittest discover -s tests -v
```
