# 亚马逊产品关键词研究

独立保存 Amazon-Skills 的 amazon-keyword-research 模块，方便学习和后续开发。包含原始 AI 研究流程说明与搜索联想词采集脚本，目前没有网页操作界面。

## 来源与授权

- 原作者：Nexscope AI
- 上游：https://github.com/nexscope-ai/Amazon-Skills
- 原始模块：https://github.com/nexscope-ai/Amazon-Skills/tree/2bcb8cb019cfac6a1e420b11f86209df5ea47686/amazon-keyword-research
- 复制版本：`2bcb8cb019cfac6a1e420b11f86209df5ea47686`
- 许可证：MIT，原始版权声明完整保存在 LICENSE。
- SKILL.md、_meta.json、scripts/research.sh 按该版本原样保留；本 README 为新增中文说明。

## 文件

| 文件 | 用途 |
| --- | --- |
| SKILL.md | 原作者给 AI 助手的研究流程 |
| scripts/research.sh | 获取亚马逊搜索联想词 |
| _meta.json | 原模块元数据 |
| LICENSE | 原作者 MIT 许可证 |

## 使用

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
- 原脚本未提供完善的超时、报错、重试和限速；失败可能被静默忽略，空结果不能证明没有需求。
- 本次仅保存源码并做 Bash 语法检查，未实测 Amazon 接口，也未安装为 AI 技能。

运营时建议结合自己的广告搜索词报表，保留来源、站点和采集日期，再按相关性、点击、订单和花费筛选。
