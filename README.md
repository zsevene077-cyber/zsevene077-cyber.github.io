# 张壮志的个人主页

个人网站：**https://zsevene077-cyber.github.io**

介绍机器人学习、AI Infra、模型评测与数据采集相关实践。中文为默认语言，提供英文版本、五个项目详情页及可打印的公开简历。

## 编辑

网站不依赖 npm、外部字体、第三方脚本或分析服务。部署的是已生成的 HTML/CSS；内容可在 JSON 中维护。

| 文件 | 内容 |
| --- | --- |
| `content/profile.json` | 个人简介、教育、经历、技术与成果，中英双语 |
| `content/projects.json` | 五条项目主线、实验条件、个人参与内容与结果边界 |
| `content/EDITING.md` | 个人信息字段说明 |
| `assets/style.css` | 布局、颜色、响应式与打印样式 |
| `assets/portrait.png` | 个人照片 |
| `build.py` | Python 标准库页面生成器 |

修改内容后，在仓库根目录运行：

```sh
python3 build.py
python3 -m http.server 8088 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8088/`，检查中文、英文及项目详情，再提交 JSON 与生成的 HTML。

项目详情使用 `projects/<id>.html` 和 `projects/<id>-en.html`。简历入口为 `cv.html` / `cv-en.html`，页面上的打印按钮可使用浏览器“另存为 PDF”。

## GitHub Pages

仓库名称保持 `zsevene077-cyber.github.io`。在 **Settings → Pages → Build and deployment** 中选择 **Deploy from a branch**，分支为 `main`，目录为 `/(root)`。保留 `.nojekyll`。

提交到发布分支后，GitHub Pages 会更新网站。发布与运行状态应以 Pages / Actions 的实际结果为准。

## 内容约定

- 这里仅保留公开脱敏介绍、公开版简历与本人照片。原始简历 PDF、电话、内部地址、任务 ID、配置、源码与实验资料不放入本仓库。
- 项目说明包括条件和适用范围。性能改进与模型成功率是不同结论；功能出分与严格验收分开记录。
- 实习职责使用“参与”“执行”“协助排查”等与实际贡献相符的表述。
- 发明专利申请与已授权外观设计专利分开标注；专利状态以更新时核验的材料为准。
- 公开项目说明目录：[embodied-ai-portfolio](https://github.com/zsevene077-cyber/embodied-ai-portfolio)。

## 文件与授权

网站代码由本人维护，个人文字、照片及项目内容保留相应权利。没有为第三方或公司的源代码授予任何许可证。相关实验材料单独管理。
