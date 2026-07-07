# 2026-07-07 同步审计记录

## 目标

- 校验 GitHub、服务器、副本目录与本地目录的一致性。
- 以可发布纯净版为目标，移除私密信息、服务器信息和个人路径依赖。
- 为后续协作保留清晰的同步记录。

## 结论

1. GitHub `main` 的核心代码文件与服务器上的“笔记副本”一致。
2. 服务器上的运行时 Skill 目录与 GitHub 不一致，且命名方式更接近 `music-creation-engine`。
3. GitHub 缺少几份协作参考文档，本地已补齐公开版。
4. 公开仓库中未发现密码、私钥、服务器地址或用户数据。

## 本次整理

- 本地目录以 GitHub `main` 内容为基线导入。
- 补充了公开版参考文档：
  - `references/architecture-report.md`
  - `references/deployment-notes.md`
  - `references/evaluation-criteria.md`
  - `references/music21-api-notes.md`
- 新增了真正项目化所需的包结构、CLI、API、适配器、示例工作流和持续开发文档。
- 统一 Skill 命名与安装路径为 `music-creation-engine`。
- 为 `install.sh` 增加 Codex 与 Hermes Creative 路径适配测试。

## 已知历史差异

- 历史安装路径曾使用 `music-creation`。
- 服务器运行时副本曾使用更精简的 Skill 目录结构。
- 历史协作文档曾引用私有笔记路径，现已改为仓库内自包含文档。

## 后续约定

- 以后新增部署说明时，不写入任何真实服务器地址、账户或绝对本机路径。
- 新增协作文档优先放在 `references/`。
- 如需变更安装路径或 Skill 名称，必须同步更新 `SKILL.md`、`install.sh`、`README.md` 和 `references/install-guide.md`。
