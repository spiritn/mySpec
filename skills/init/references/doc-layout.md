# 文档目录参考

根目录支持 `docs/` 和 `doc/`。下列子目录参考旧版按产品、模块、项目约束和需求迭代组织知识的做法。子目录是整理新文档的备选，已有文档沿用当前路径和粒度。

| 分类 | 典型子目录或入口 | 读取时机 |
| --- | --- | --- |
| `backend/` | `architecture/` 架构与模块边界，`domain/` 领域与实体，`api/` 接口与事件，`data/` 数据模型，`decisions/` 技术决策 | 后端设计、改接口或数据、评审服务影响 |
| `prd/` | 产品概览、`modules/` 功能规格、`flows/` 业务流程、术语和角色 | 澄清需求、核对用户流程和验收 |
| `rules/` | `engineering/` 工程约定，`business/` 业务约束，`pitfalls/` 已确认的踩坑经验 | 设计、实现和评审前查适用约束 |
| `fronted/` 或 `frontend/` | `architecture/` 前端架构，`pages/` 页面与路由，`components/` 组件，`integration/` 接口集成 | 页面、交互、状态和前后端契约变更 |
| `deploy/` | `environments/` 环境差异，`release/` 发布回滚，`runbooks/` 操作手册 | 涉及环境、数据库迁移、发布或排障 |
| `changes/` | `<work-item>/` 存放正在实施的需求、设计、任务、验证和评审资料，`archive/` 存放收尾后的工单。已有 `increment/` 或按状态分组的项目沿用实际路径 | 按工单恢复任务、复查设计或查历史变更 |

显式要求新建目录且无项目约定时，顶层采用 `backend/`、`prd/`、`rules/`、`fronted/`、`deploy/`、`changes/`。已有 `frontend/` 时沿用。只有实际有内容或明确需要的专题才细分子目录。
