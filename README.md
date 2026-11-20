# 张壮志的个人主页

个人网站：**https://zsevene077-cyber.github.io**

介绍机器人学习、AI Infra、模型评测与数据采集相关实践。中文为默认语言，提供英文版本、五个项目详情页及可打印的公开简历。

## 编辑

网站不依赖 npm、外部字体、第三方脚本或分析服务。部署的是已生成的 HTML/CSS；内容可在 JSON 中维护。

| 文件 | 内容 |
| --- | --- |
| `content/profile.json` | 个人简介、教育、经历、技术与成果，中英双语 |
| `content/projects.json` | 五条项目主线、实验条件、个人参与内容与结果边界 |
| `content/media.json` | 可选的项目缩略图、图集和短视频；空配置继续显示图表 |
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

## 补充项目图片与短视频

将准备公开的真实素材放到 `assets/media/`，例如 `assets/media/vla-evaluation/demo.mp4`。目前各项目的 `thumbnail` 为 `null`，`gallery` 为空数组：页面保持现有图表，不显示空位。

在 `content/media.json` 中找到对应的项目 ID，填写下面结构。这里的路径仅用于说明；先放入实际文件，再使用配置。

```json
"vla-evaluation": {
  "thumbnail": {
    "type": "image",
    "src": "assets/media/vla-evaluation/overview.webp",
    "alt": { "zh": "画面中实际展示的环境与任务", "en": "The actual environment and task shown" },
    "caption": { "zh": "环境、任务及演示条件", "en": "Environment, task, and demonstration conditions" }
  },
  "gallery": [
    {
      "type": "video",
      "src": "assets/media/vla-evaluation/demo.mp4",
      "poster": "assets/media/vla-evaluation/poster.webp",
      "alt": { "zh": "视频内容的简短描述", "en": "A brief description of the video" },
      "caption": { "zh": "一次实际演示；注明模型和任务", "en": "An actual demonstration; identify the model and task" }
    }
  ]
}
```

- `thumbnail` 控制首页项目图，可使用 `image` 或 `video`；设回 `null` 恢复图表。
- `gallery` 依次显示在项目详情中，可混合图片和视频；为空时整个影像区不出现，原有结果图表保留。
- `alt` 与 `caption` 各有 `zh` / `en`。`alt` 必须描述实际画面；无需图注时可将 `caption` 的两个值设为空字符串。
- 视频的 `poster` 可省略；播放器提供控制栏，只预载元数据，不自动播放。
- 支持 JPG、PNG、WebP、AVIF、GIF，以及 MP4、WebM；只引用 `assets/media/` 内的本地文件，不嵌入外部网站。
- 配置完成后运行 `python3 build.py`。缺失文件、外部链接、无效项目 ID 或缺少双语说明会在生成时提示，修正后再提交。

建议优先准备这些素材：

| 优先级 | 素材 | 用途 | 建议 |
| --- | --- | --- | --- |
| 首先 | VLA 仿真任务截图 1–2 张，或短视频 1 段 | 展示评测实际运行的环境与任务 | 横图约 16:9，注明模拟器、任务与模型；短片 10–20 秒 |
| 首先 | NexArm 采集装置全景 1 张、相机与机械臂配合画面 1 张 | 让读者看懂真实采集系统 | 光线清楚，保留设备关系；去除无关人员和敏感标识 |
| 首先 | 评测平台界面截图 1–2 张 | 展示任务状态或结果组织 | 保留界面文字可读，遮去内部地址、账号、任务 ID 和配置值 |
| 其次 | VLM 评测或训练回归的自制结果图 1 张 | 补充任务覆盖或回归过程 | 使用可公开的汇总数据，标明范围与日期 |
| 可选 | 更适合主页的个人照片 | 替换现有简历照片 | 当前照片可继续用，不是首版的必需补件 |

图片建议长边 1600–2400 像素，单张压缩至约 1 MB；短视频建议 H.264 MP4、720p 或 1080p、单段约 10 MB 以内。首页缩略图按 16:10 裁切，详情图保留画面比例。若有需要展示的文字或边缘细节，把该图放入详情图集。无需提供专利证书或内部模型截图。

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
