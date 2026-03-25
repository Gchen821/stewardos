# Web App

`apps/web` 是 StewardOS 当前已经初始化完成的前端应用，技术栈为 Next.js 16 + React 19 + TypeScript + Tailwind CSS 4。

## 本地开发

先安装依赖，再启动开发服务器：

```bash
corepack enable
pnpm dev
```

如果尚未安装依赖，先执行：

```bash
pnpm install
```

访问地址：`http://localhost:3000`

## 目录说明

- `src/app`: App Router 页面入口
- `public`: 静态资源
- `eslint.config.mjs`: ESLint 配置
- `next.config.ts`: Next.js 配置
- `tsconfig.json`: TypeScript 配置

## 说明

- 当前页面还是默认模板，需要后续替换成平台首页和业务路由
- 如果从仓库根目录启动，请优先参考根级 [README.md](/home/gc/project/StewardOS/README.md)

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
