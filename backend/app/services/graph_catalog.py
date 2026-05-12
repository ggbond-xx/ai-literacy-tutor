CATALOG_CONCEPTS = [
    {
        "slug": "ai-basics",
        "name": "人工智能基础",
        "description": "理解人工智能的定义、核心能力边界、发展历程与典型应用场景。",
        "category": "基础概念",
        "difficulty": 1,
        "estimated_minutes": 20,
        "key_points": [
            "区分弱人工智能与通用人工智能",
            "理解感知、判断、生成三类典型能力",
            "认识 AI 与数字素养课程的关系",
        ],
        "text_material": "学习这一节点时，先建立“AI 能做什么、不能做什么”的认识，再结合推荐系统、语音助手和生成式模型去理解应用边界。",
        "image_url": "/materials/foundation-map.svg",
        "video_title": "推荐检索词：人工智能基础 课程导学",
        "video_url": "https://search.bilibili.com/all?keyword=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%9F%BA%E7%A1%80%20%E8%AF%BE%E7%A8%8B%E5%AF%BC%E5%AD%A6",
        "resource_links": [
            {"label": "AI 应用案例检索", "url": "https://search.bilibili.com/all?keyword=AI%20%E5%BA%94%E7%94%A8%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "下列哪项更接近人工智能基础的准确理解？",
                "options": [
                    "AI 只等于机器人",
                    "AI 是让机器具备部分感知、判断或生成能力的技术集合",
                    "AI 只能用于编程课",
                    "AI 一定会完全代替老师",
                ],
                "answer_index": 1,
                "explanation": "人工智能是多种算法与计算能力的组合，不局限于机器人或某一学科。",
            },
            {
                "question": "在助学场景里，对 AI 输出更合理的态度是？",
                "options": [
                    "默认所有结果都正确",
                    "输出后不再验证",
                    "结合任务背景和资料来源进行核验",
                    "只看答案不看过程",
                ],
                "answer_index": 2,
                "explanation": "数字素养强调会用也会辨，需要结合场景和资料进行验证。",
            },
        ],
    },
    {
        "slug": "algorithmic-thinking",
        "name": "算法思维",
        "description": "从问题拆解、流程设计、规则表达等角度理解算法思维。",
        "category": "基础概念",
        "difficulty": 1,
        "estimated_minutes": 25,
        "key_points": [
            "学会把复杂任务拆成可执行步骤",
            "理解输入、处理、输出的基本流程",
            "建立规则化表达意识",
        ],
        "text_material": "算法思维并不等于写代码，它更像一种结构化解决问题的能力，是理解后续提示词设计与机器学习的前提。",
        "image_url": "/materials/process-logic.svg",
        "video_title": "推荐检索词：算法思维 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%AE%97%E6%B3%95%E6%80%9D%E7%BB%B4%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "流程图与问题拆解案例", "url": "https://search.bilibili.com/all?keyword=%E6%B5%81%E7%A8%8B%E5%9B%BE%20%E9%97%AE%E9%A2%98%E6%8B%86%E8%A7%A3"},
        ],
        "quiz": [
            {
                "question": "算法思维最核心的特点之一是？",
                "options": ["结构化拆解任务", "随机猜测答案", "忽略步骤顺序", "只看结果不看过程"],
                "answer_index": 0,
                "explanation": "算法思维强调对问题进行结构化拆解与流程表达。",
            },
            {
                "question": "面对复杂学习任务，先明确目标和输入条件的价值在于？",
                "options": ["减少思考", "便于后续设计解决流程", "跳过分析阶段", "只为记忆术语"],
                "answer_index": 1,
                "explanation": "明确目标和输入条件是构建解决流程的前提。",
            },
        ],
    },
    {
        "slug": "data-literacy",
        "name": "数据素养",
        "description": "了解数据获取、清洗、分析、解读与隐私保护等核心能力。",
        "category": "数字素养",
        "difficulty": 2,
        "estimated_minutes": 30,
        "key_points": [
            "理解结构化与非结构化数据差异",
            "认识数据偏差与采样风险",
            "形成隐私保护与合规意识",
        ],
        "text_material": "数据素养是学习 AI 的地基。比起单纯会搜数据，更重要的是会判断数据质量、理解数据来源，并在使用过程中保护个人信息。",
        "image_url": "/materials/data-cycle.svg",
        "video_title": "推荐检索词：数据素养 数字公民",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E6%8D%AE%E7%B4%A0%E5%85%BB%20%E6%95%B0%E5%AD%97%E5%85%AC%E6%B0%91",
        "resource_links": [
            {"label": "数据分析基础检索", "url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%20%E5%9F%BA%E7%A1%80"},
        ],
        "quiz": [
            {
                "question": "数据素养最强调的能力之一是？",
                "options": ["只会收集数据", "判断数据来源与质量", "只会做图表", "只背术语"],
                "answer_index": 1,
                "explanation": "会评估数据质量与适用性，是数据素养的重要能力。",
            },
            {
                "question": "以下哪项更符合隐私保护意识？",
                "options": ["公开分享全部原始数据", "使用最小必要原则处理个人信息", "忽略数据来源", "复制全部数据备用"],
                "answer_index": 1,
                "explanation": "数字素养强调合法、合规、适度地处理数据。",
            },
        ],
    },
    {
        "slug": "data-cleaning",
        "name": "数据采集与清洗",
        "description": "掌握数据采集流程、异常值处理、缺失值处理和格式统一。",
        "category": "数字素养",
        "difficulty": 2,
        "estimated_minutes": 30,
        "key_points": [
            "了解采集、标注、清洗的基本流程",
            "识别异常值和缺失值处理方式",
            "理解数据一致性的重要性",
        ],
        "text_material": "模型表现不佳，很多时候不是算法本身的问题，而是前期数据准备不足。学习这一节点能帮助学生建立数据准备意识。",
        "image_url": "/materials/data-cycle.svg",
        "video_title": "推荐检索词：数据清洗 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E6%8D%AE%E6%B8%85%E6%B4%97%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "缺失值处理案例", "url": "https://search.bilibili.com/all?keyword=%E7%BC%BA%E5%A4%B1%E5%80%BC%20%E5%A4%84%E7%90%86"},
        ],
        "quiz": [
            {
                "question": "数据清洗的目标之一是？",
                "options": ["增加噪声", "让数据更一致可用", "忽略异常值", "随机删列"],
                "answer_index": 1,
                "explanation": "清洗的核心目标是提升数据质量和后续分析的可靠性。",
            },
            {
                "question": "面对缺失值时更合理的第一步是？",
                "options": ["直接训练模型", "分析缺失原因并选择处理策略", "全部替换为 0", "删除全部字段"],
                "answer_index": 1,
                "explanation": "不同缺失原因对应不同处理方式，不能机械套用。",
            },
        ],
    },
    {
        "slug": "machine-learning",
        "name": "机器学习",
        "description": "掌握监督学习、无监督学习、特征与模型训练的基本概念。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 40,
        "key_points": [
            "理解训练集、验证集、测试集的作用",
            "区分分类、回归、聚类等任务",
            "建立特征与标签意识",
        ],
        "text_material": "理解机器学习时，不必先沉迷复杂公式，先抓住任务类型、训练流程和评价指标，再逐步过渡到模型原理。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：机器学习 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "机器学习课程检索", "url": "https://www.coursera.org/search?query=machine%20learning"},
        ],
        "quiz": [
            {
                "question": "监督学习最典型的特征是？",
                "options": ["没有标签", "训练数据包含输入与对应标签", "只依赖人工规则", "不需要数据"],
                "answer_index": 1,
                "explanation": "监督学习需要带标签的数据来建立输入与输出的映射。",
            },
            {
                "question": "测试集的主要作用是？",
                "options": ["训练参数", "最终评估模型泛化效果", "生成标签", "清洗数据"],
                "answer_index": 1,
                "explanation": "测试集常用于评估模型在未见数据上的表现。",
            },
        ],
    },
    {
        "slug": "supervised-learning",
        "name": "监督学习",
        "description": "理解有标签数据驱动下的分类与回归任务。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "区分分类与回归任务",
            "理解标签对学习过程的意义",
            "会解释常见应用场景",
        ],
        "text_material": "监督学习是多数识别、预测任务的基础。重点是理解‘有标签样本如何帮助模型学会映射关系’。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：监督学习 分类 回归",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%9B%91%E7%9D%A3%E5%AD%A6%E4%B9%A0%20%E5%88%86%E7%B1%BB%20%E5%9B%9E%E5%BD%92",
        "resource_links": [
            {"label": "分类任务案例", "url": "https://search.bilibili.com/all?keyword=%E5%88%86%E7%B1%BB%E4%BB%BB%E5%8A%A1%20AI"},
        ],
        "quiz": [
            {
                "question": "垃圾邮件识别更接近哪类监督学习任务？",
                "options": ["回归", "分类", "聚类", "强化学习"],
                "answer_index": 1,
                "explanation": "垃圾邮件识别通常是在多个类别中做判断，因此属于分类任务。",
            },
            {
                "question": "监督学习中的标签可以理解为？",
                "options": ["随机编号", "输入样本的正确答案或目标值", "模型参数", "测试误差"],
                "answer_index": 1,
                "explanation": "标签是训练监督信号的来源。",
            },
        ],
    },
    {
        "slug": "unsupervised-learning",
        "name": "无监督学习",
        "description": "理解聚类、降维等无标签学习方式及其应用。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "知道无标签数据的典型处理方式",
            "理解聚类的基本思想",
            "认识无监督学习的局限性",
        ],
        "text_material": "无监督学习常用于探索数据中的潜在结构和相似性，适合没有明确标签时的先行分析。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：无监督学习 聚类",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%97%A0%E7%9B%91%E7%9D%A3%E5%AD%A6%E4%B9%A0%20%E8%81%9A%E7%B1%BB",
        "resource_links": [
            {"label": "聚类案例检索", "url": "https://search.bilibili.com/all?keyword=%E8%81%9A%E7%B1%BB%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "无监督学习最典型的场景之一是？",
                "options": ["图像分类已知标签训练", "用户群体聚类分析", "已知答案回归预测", "人工标注数据"],
                "answer_index": 1,
                "explanation": "聚类是典型的无监督学习任务，用于挖掘数据结构。",
            },
            {
                "question": "无监督学习常用于探索性分析，是因为？",
                "options": ["它不需要任何数据", "它能在缺少标签时帮助发现模式", "它一定更准确", "它只适用于图像"],
                "answer_index": 1,
                "explanation": "在标签缺失或昂贵时，无监督学习适合先探索结构。",
            },
        ],
    },
    {
        "slug": "model-evaluation",
        "name": "模型评估",
        "description": "通过准确率、召回率、泛化能力等指标评价模型效果。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 30,
        "key_points": [
            "理解准确率与召回率的区别",
            "认识过拟合和欠拟合",
            "知道为什么要做交叉验证",
        ],
        "text_material": "模型评估帮助学生建立‘结果不只看单一分数’的意识。尤其在教育场景中，误判成本与解释性同样重要。",
        "image_url": "/materials/evaluation-matrix.svg",
        "video_title": "推荐检索词：模型评估 准确率 召回率",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%A8%A1%E5%9E%8B%E8%AF%84%E4%BC%B0%20%E5%87%86%E7%A1%AE%E7%8E%87%20%E5%8F%AC%E5%9B%9E%E7%8E%87",
        "resource_links": [
            {"label": "混淆矩阵示例", "url": "https://search.bilibili.com/all?keyword=%E6%B7%B7%E6%B7%86%E7%9F%A9%E9%98%B5"},
        ],
        "quiz": [
            {
                "question": "模型只在训练集表现很好，换新数据效果差，这通常叫？",
                "options": ["欠拟合", "过拟合", "聚类", "泛化增强"],
                "answer_index": 1,
                "explanation": "过拟合表示模型过度记忆训练数据，泛化能力不足。",
            },
            {
                "question": "当漏检高风险样本代价较大时，更应关注哪类指标？",
                "options": ["召回率", "界面配色", "节点数量", "文本长度"],
                "answer_index": 0,
                "explanation": "当漏检代价高时，召回率往往是更关键的评价指标。",
            },
        ],
    },
    {
        "slug": "ai-ethics",
        "name": "AI伦理与治理",
        "description": "认识算法偏见、透明性、责任归属与治理框架。",
        "category": "伦理素养",
        "difficulty": 2,
        "estimated_minutes": 25,
        "key_points": [
            "识别数据偏差与算法歧视风险",
            "理解透明性、可解释性与责任归属",
            "建立负责任使用 AI 的意识",
        ],
        "text_material": "伦理与治理不是附属话题，而是数字素养课程中的关键能力，决定了学生是否能在真实场景中安全、负责地应用 AI。",
        "image_url": "/materials/ethics-balance.svg",
        "video_title": "推荐检索词：AI伦理 算法偏见",
        "video_url": "https://search.bilibili.com/all?keyword=AI%E4%BC%A6%E7%90%86%20%E7%AE%97%E6%B3%95%E5%81%8F%E8%A7%81",
        "resource_links": [
            {"label": "算法偏见主题检索", "url": "https://search.bilibili.com/all?keyword=%E7%AE%97%E6%B3%95%E5%81%8F%E8%A7%81"},
        ],
        "quiz": [
            {
                "question": "哪项最能体现 AI 伦理意识？",
                "options": ["忽略训练数据偏差", "使用 AI 时设置人工复核", "默认模型绝对公平", "只关注运行速度"],
                "answer_index": 1,
                "explanation": "伦理意识强调边界、责任和人机协作机制。",
            },
            {
                "question": "可解释性的核心意义之一是？",
                "options": ["让用户理解模型判断依据", "让界面更复杂", "隐藏数据来源", "减少训练数据"],
                "answer_index": 0,
                "explanation": "可解释性帮助使用者理解结果来源，提高可信度和可追责性。",
            },
        ],
    },
    {
        "slug": "digital-safety",
        "name": "信息甄别与数字安全",
        "description": "提升信息辨识、账号安全、隐私保护和网络风险应对能力。",
        "category": "数字素养",
        "difficulty": 2,
        "estimated_minutes": 20,
        "key_points": [
            "判断 AI 生成内容的真实性",
            "理解账号与密码安全基本规则",
            "知道常见网络诈骗与信息污染方式",
        ],
        "text_material": "在生成式 AI 时代，学生不仅要会用工具，还要会辨识内容、保护账号和防范信息误导，这正是数字素养的现实延伸。",
        "image_url": "/materials/safety-shield.svg",
        "video_title": "推荐检索词：数字安全 信息甄别",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E5%AD%97%E5%AE%89%E5%85%A8%20%E4%BF%A1%E6%81%AF%E7%94%84%E5%88%AB",
        "resource_links": [
            {"label": "网络安全素养检索", "url": "https://search.bilibili.com/all?keyword=%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%20%E7%B4%A0%E5%85%BB"},
        ],
        "quiz": [
            {
                "question": "面对来源不明的 AI 生成截图，第一步更合理的是？",
                "options": ["立即转发", "核对来源与上下文", "默认真实", "忽略账号安全"],
                "answer_index": 1,
                "explanation": "信息甄别强调来源校验、上下文核查和多源交叉验证。",
            },
            {
                "question": "哪项属于数字安全良好习惯？",
                "options": ["多个平台使用同一弱密码", "打开来路不明链接", "定期更换高强度密码并启用双重验证", "公开分享验证码"],
                "answer_index": 2,
                "explanation": "强密码与多重验证是数字安全的基础措施。",
            },
        ],
    },
    {
        "slug": "prompt-design",
        "name": "提示词设计",
        "description": "掌握目标明确、结构清晰、上下文充分的提示词构建方法。",
        "category": "应用实践",
        "difficulty": 2,
        "estimated_minutes": 25,
        "key_points": [
            "明确任务、角色、输出格式",
            "通过示例提升输出质量",
            "理解迭代提示与约束条件",
        ],
        "text_material": "提示词设计不是神秘咒语，而是清晰表达任务目标、约束与输出要求的沟通能力，它与算法思维紧密相关。",
        "image_url": "/materials/prompt-stack.svg",
        "video_title": "推荐检索词：提示词工程 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%8F%90%E7%A4%BA%E8%AF%8D%E5%B7%A5%E7%A8%8B%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "提示词案例合集", "url": "https://search.bilibili.com/all?keyword=%E6%8F%90%E7%A4%BA%E8%AF%8D%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "高质量提示词通常不包括哪一项？",
                "options": ["明确任务目标", "限制输出格式", "提供必要背景", "完全不给上下文"],
                "answer_index": 3,
                "explanation": "缺乏上下文会让模型更难理解需求。",
            },
            {
                "question": "当模型输出不符合预期时，更好的做法是？",
                "options": ["停止使用", "逐步补充约束条件和示例", "随机复制别人的提示词", "忽略结果质量"],
                "answer_index": 1,
                "explanation": "提示词设计强调迭代与反馈修正。",
            },
        ],
    },
    {
        "slug": "generative-ai",
        "name": "生成式AI应用",
        "description": "理解大模型在文本、图像、学习辅导等场景中的典型应用与风险控制。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "知道生成式 AI 的典型能力边界",
            "理解多轮对话和内容生成场景",
            "会结合伦理与安全意识使用模型",
        ],
        "text_material": "生成式 AI 是本课程最具应用感的部分，但重点不是让模型替你完成学习，而是学会用它辅助学习、创作和反思。",
        "image_url": "/materials/generative-workflow.svg",
        "video_title": "推荐检索词：生成式AI 学习应用",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%94%9F%E6%88%90%E5%BC%8FAI%20%E5%AD%A6%E4%B9%A0%E5%BA%94%E7%94%A8",
        "resource_links": [
            {"label": "生成式 AI 应用案例", "url": "https://search.bilibili.com/all?keyword=%E7%94%9F%E6%88%90%E5%BC%8FAI%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "生成式 AI 在助学场景中的合理定位更接近？",
                "options": ["代替学生思考", "提供启发、解释与反馈支持", "保证所有答案绝对准确", "完全跳过学习过程"],
                "answer_index": 1,
                "explanation": "助学系统强调的是辅助学习，而不是替代学习。",
            },
            {
                "question": "使用生成式 AI 时为何仍需核验内容？",
                "options": ["模型可能产生幻觉或过时信息", "AI 永远离线", "模型不会生成文本", "所有输出都一样"],
                "answer_index": 0,
                "explanation": "模型输出仍可能存在事实错误、幻觉或上下文偏差，需要学习者主动校验。",
            },
        ],
    },
    {
        "slug": "human-ai-collaboration",
        "name": "人机协同实践",
        "description": "通过案例化任务理解人机协同分工、验证与优化流程。",
        "category": "应用实践",
        "difficulty": 2,
        "estimated_minutes": 30,
        "key_points": [
            "学会判断哪些任务适合交给 AI 辅助",
            "形成“生成 - 评估 - 修正”协同流程",
            "认识人类在价值判断与结果把关中的作用",
        ],
        "text_material": "把 AI 真正用于助学，不是一次性生成最终答案，而是在任务规划、资料整理、表达优化和复盘反思等环节进行人机协同。",
        "image_url": "/materials/generative-workflow.svg",
        "video_title": "推荐检索词：人机协同 学习任务",
        "video_url": "https://search.bilibili.com/all?keyword=%E4%BA%BA%E6%9C%BA%E5%8D%8F%E5%90%8C%20%E5%AD%A6%E4%B9%A0%E4%BB%BB%E5%8A%A1",
        "resource_links": [
            {"label": "人机协同案例检索", "url": "https://search.bilibili.com/all?keyword=%E4%BA%BA%E6%9C%BA%E5%8D%8F%E5%90%8C%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "在人机协同学习流程中，最适合由学生主导的环节之一是？",
                "options": ["价值判断与结果核验", "完全不参与", "所有结论都交给模型", "忽略上下文"],
                "answer_index": 0,
                "explanation": "学生仍需负责目标设定、结果判断与最终输出把关。",
            },
            {
                "question": "以下哪种做法最体现有效的人机协同？",
                "options": ["模型生成后不再检查", "学生给出目标，AI 辅助生成，学生再校验与修改", "完全复制 AI 输出", "跳过任务目标"],
                "answer_index": 1,
                "explanation": "有效的人机协同强调分工、复核和迭代改进。",
            },
        ],
    },
    {
        "slug": "neural-network",
        "name": "神经网络基础",
        "description": "了解神经网络层、激活函数和从样本中提取特征的基本机制。",
        "category": "算法模型",
        "difficulty": 4,
        "estimated_minutes": 40,
        "key_points": [
            "理解输入层、隐藏层、输出层的结构",
            "认识参数训练与特征提取的关系",
            "知道神经网络为何适合处理复杂模式",
        ],
        "text_material": "神经网络可以理解为一种多层表示学习方式，它让模型能够逐步抽取更复杂的特征，是现代视觉和语言模型的重要基础。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：神经网络基础 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "神经网络可视化案例", "url": "https://search.bilibili.com/all?keyword=%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%20%E5%8F%AF%E8%A7%86%E5%8C%96"},
        ],
        "quiz": [
            {
                "question": "神经网络中隐藏层的主要价值之一是？",
                "options": ["存储用户名", "逐层提取更抽象的特征", "取代所有数据清洗", "让模型不再需要训练"],
                "answer_index": 1,
                "explanation": "隐藏层有助于模型从输入中逐步学习更高层次的表示。",
            },
            {
                "question": "神经网络常被用于处理复杂模式，是因为？",
                "options": ["完全不依赖数据", "能够通过多层参数学习非线性关系", "不需要任何算力", "只能处理表格数据"],
                "answer_index": 1,
                "explanation": "多层结构使神经网络更擅长逼近复杂的非线性映射关系。",
            },
        ],
    },
    {
        "slug": "computer-vision",
        "name": "计算机视觉",
        "description": "理解图像分类、目标检测等视觉任务，以及 AI 如何“看懂”图像。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 30,
        "key_points": [
            "理解图像分类与目标检测差异",
            "知道数据标注对视觉任务的重要性",
            "认识视觉模型在教育和生活中的应用",
        ],
        "text_material": "计算机视觉让 AI 可以从图片、视频中识别目标和场景。在校园场景中，它可用于实验识别、安防辅助和图像检索等任务。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：计算机视觉 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E8%AE%A1%E7%AE%97%E6%9C%BA%E8%A7%86%E8%A7%89%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "图像分类案例检索", "url": "https://search.bilibili.com/all?keyword=%E5%9B%BE%E5%83%8F%E5%88%86%E7%B1%BB%20AI"},
        ],
        "quiz": [
            {
                "question": "“判断一张图片是不是猫”更接近哪类视觉任务？",
                "options": ["图像分类", "情感分析", "推荐排序", "密码加密"],
                "answer_index": 0,
                "explanation": "图像分类关注的是给整张图像分配类别标签。",
            },
            {
                "question": "目标检测相较于图像分类，多关注什么信息？",
                "options": ["图片的颜色数量", "目标的位置与边界", "文本长度", "浏览器版本"],
                "answer_index": 1,
                "explanation": "目标检测不仅要判断类别，还要识别对象出现的位置。",
            },
        ],
    },
    {
        "slug": "natural-language-processing",
        "name": "自然语言处理",
        "description": "理解文本分类、问答、摘要与对话系统背后的语言处理思路。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "知道分词、表示学习与上下文建模的基本作用",
            "理解文本分类与问答任务的差异",
            "认识 NLP 与生成式 AI 的联系",
        ],
        "text_material": "自然语言处理关注如何让机器理解和生成自然语言。对助学系统而言，问答、摘要、作文反馈等能力都与 NLP 密切相关。",
        "image_url": "/materials/prompt-stack.svg",
        "video_title": "推荐检索词：自然语言处理 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "NLP 任务案例检索", "url": "https://search.bilibili.com/all?keyword=NLP%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "自动生成文章摘要更接近哪类能力？",
                "options": ["文本理解与生成", "图像识别", "网络爬虫", "硬件调试"],
                "answer_index": 0,
                "explanation": "摘要任务本质上属于自然语言处理中的文本生成与压缩表达。",
            },
            {
                "question": "助学问答系统与哪类 AI 能力关系最紧密？",
                "options": ["自然语言处理", "仅计算机视觉", "数据库备份", "三维建模"],
                "answer_index": 0,
                "explanation": "问答系统依赖文本理解、检索与生成等 NLP 能力。",
            },
        ],
    },
    {
        "slug": "multimodal-ai",
        "name": "多模态AI",
        "description": "认识文本、图像、音频等多种模态融合处理的学习与应用场景。",
        "category": "应用实践",
        "difficulty": 4,
        "estimated_minutes": 35,
        "key_points": [
            "理解多模态输入与输出的基本概念",
            "知道图文联合理解的典型应用",
            "认识多模态系统的真实性和安全风险",
        ],
        "text_material": "多模态 AI 把文字、图像、语音等信息联合起来处理，是当前生成式 AI 发展的重要方向，也更贴近真实学习场景中的资料形式。",
        "image_url": "/materials/generative-workflow.svg",
        "video_title": "推荐检索词：多模态AI 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E5%A4%9A%E6%A8%A1%E6%80%81AI%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "图文理解案例检索", "url": "https://search.bilibili.com/all?keyword=%E5%9B%BE%E6%96%87%E7%90%86%E8%A7%A3%20AI"},
        ],
        "quiz": [
            {
                "question": "多模态 AI 的典型特点是？",
                "options": ["只能输入文字", "可以联合处理图像、文本等多种信息", "完全不需要提示词", "不涉及任何风险"],
                "answer_index": 1,
                "explanation": "多模态系统的核心就是跨多种信息形式进行联合理解和生成。",
            },
            {
                "question": "下面哪个场景更能体现多模态能力？",
                "options": ["只对表格做加法", "上传图片并让模型生成讲解文字", "只修改密码", "只导出日志"],
                "answer_index": 1,
                "explanation": "图像输入加文字输出就是典型的多模态处理场景。",
            },
        ],
    },
    {
        "slug": "ai-project-learning",
        "name": "AI项目式学习",
        "description": "围绕真实任务完成选题、资料收集、方案设计、实现展示与复盘优化。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 45,
        "key_points": [
            "明确项目目标与评价标准",
            "结合图谱知识完成任务分解和资源整合",
            "学会在复盘中总结问题与改进策略",
        ],
        "text_material": "项目式学习是把课程知识真正串起来的阶段。学生需要结合知识图谱、提示词设计和自测反馈，完成一个能展示思考过程的 AI 学习项目。",
        "image_url": "/materials/process-logic.svg",
        "video_title": "推荐检索词：AI 项目式学习 案例",
        "video_url": "https://search.bilibili.com/all?keyword=AI%20%E9%A1%B9%E7%9B%AE%E5%BC%8F%E5%AD%A6%E4%B9%A0",
        "resource_links": [
            {"label": "课程项目案例检索", "url": "https://search.bilibili.com/all?keyword=%E8%AF%BE%E7%A8%8B%E9%A1%B9%E7%9B%AE%20AI"},
        ],
        "quiz": [
            {
                "question": "项目式学习最关键的特点之一是？",
                "options": ["只抄现成答案", "围绕真实任务组织学习过程", "完全不需要复盘", "跳过方案设计"],
                "answer_index": 1,
                "explanation": "项目式学习强调任务驱动、过程性产出和综合能力训练。",
            },
            {
                "question": "在 AI 项目复盘时，更有价值的做法是？",
                "options": ["只展示成功结果", "分析问题、记录修改过程并总结经验", "删除全部草稿", "忽略失败原因"],
                "answer_index": 1,
                "explanation": "复盘的价值在于暴露问题、沉淀经验，并为下一轮改进提供依据。",
            },
        ],
    },
    {
        "slug": "knowledge-representation",
        "name": "知识表示与推理",
        "description": "理解如何把知识转化为规则、符号与结构，并基于此进行推理判断。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "认识事实、规则与关系的表示方式",
            "理解推理在问答与专家系统中的作用",
            "知道符号方法与数据驱动方法的差异",
        ],
        "text_material": "知识表示与推理强调把经验知识组织成机器可处理的结构，再通过规则推导出结论。学习这一节点有助于理解智能系统不只依赖数据训练，也可以依赖显式知识。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：知识表示与推理 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%9F%A5%E8%AF%86%E8%A1%A8%E7%A4%BA%E4%B8%8E%E6%8E%A8%E7%90%86%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "规则系统案例检索", "url": "https://search.bilibili.com/all?keyword=%E8%A7%84%E5%88%99%E7%B3%BB%E7%BB%9F%20AI"},
        ],
        "quiz": [
            {
                "question": "知识表示与推理更强调哪类能力？",
                "options": ["把知识组织成结构并进行规则推断", "只做图片美化", "只负责数据库备份", "完全不需要任何关系结构"],
                "answer_index": 0,
                "explanation": "这一方向的核心是让机器能够存储知识并据此做出推理。 ",
            },
            {
                "question": "专家系统和知识图谱应用都与哪项能力关系较大？",
                "options": ["知识表示与推理", "前端排版", "账号注册", "视频剪辑"],
                "answer_index": 0,
                "explanation": "知识结构化与规则推断是这类系统的重要基础。",
            },
        ],
    },
    {
        "slug": "open-dataset-search",
        "name": "开源数据集检索",
        "description": "学习如何寻找公开数据集、判断可用性，并记录数据来源与授权信息。",
        "category": "数字素养",
        "difficulty": 2,
        "estimated_minutes": 25,
        "key_points": [
            "会用关键词和筛选条件检索数据集",
            "关注数据规模、标签质量和授权方式",
            "形成来源记录与引用意识",
        ],
        "text_material": "很多学习项目卡在“没有合适数据”。掌握数据集检索后，学生能更快找到符合任务需求的公开样本，并学会判断数据是否可用于课堂项目。",
        "image_url": "/materials/data-cycle.svg",
        "video_title": "推荐检索词：开源数据集 检索",
        "video_url": "https://search.bilibili.com/all?keyword=%E5%BC%80%E6%BA%90%E6%95%B0%E6%8D%AE%E9%9B%86%20%E6%A3%80%E7%B4%A2",
        "resource_links": [
            {"label": "数据集搜索方法检索", "url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E6%8D%AE%E9%9B%86%20%E6%90%9C%E7%B4%A2%20%E6%95%99%E7%A8%8B"},
        ],
        "quiz": [
            {
                "question": "检索开源数据集时更应该优先关注哪项信息？",
                "options": ["来源、标签质量与授权方式", "页面颜色", "下载按钮大小", "评论数量"],
                "answer_index": 0,
                "explanation": "数据来源、质量和授权条件直接决定数据能否安全使用。",
            },
            {
                "question": "找到数据集后，为什么要记录来源链接？",
                "options": ["便于后续引用、复核和说明数据合法性", "为了截图更好看", "为了隐藏出处", "没有实际必要"],
                "answer_index": 0,
                "explanation": "记录来源是数据素养和学术规范的重要部分。",
            },
        ],
    },
    {
        "slug": "feature-engineering",
        "name": "特征工程",
        "description": "理解特征选择、特征构造与特征变换对模型效果的影响。",
        "category": "算法模型",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "知道什么是有效特征",
            "理解特征构造与特征筛选思路",
            "认识特征质量对模型表现的作用",
        ],
        "text_material": "特征工程帮助学生理解：模型效果不只取决于算法，输入给模型的特征质量同样关键。很多看似复杂的问题，其实是特征表达还不够好。",
        "image_url": "/materials/model-map.svg",
        "video_title": "推荐检索词：特征工程 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E7%89%B9%E5%BE%81%E5%B7%A5%E7%A8%8B%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "特征选择案例检索", "url": "https://search.bilibili.com/all?keyword=%E7%89%B9%E5%BE%81%E9%80%89%E6%8B%A9%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "特征工程最主要是在优化什么？",
                "options": ["模型输入信息的表达质量", "电脑风扇转速", "浏览器缓存", "页面背景色"],
                "answer_index": 0,
                "explanation": "特征工程处理的是模型输入如何更好地表达任务信息。",
            },
            {
                "question": "下面哪项更像特征工程的任务？",
                "options": ["把原始字段转换成更有判别力的特征", "删除所有数据", "只修改账号密码", "关闭网络连接"],
                "answer_index": 0,
                "explanation": "特征工程强调构造、筛选和变换特征，以提升模型效果。",
            },
        ],
    },
    {
        "slug": "reinforcement-learning",
        "name": "强化学习",
        "description": "理解智能体如何在环境反馈中通过奖励信号不断优化行为策略。",
        "category": "算法模型",
        "difficulty": 4,
        "estimated_minutes": 40,
        "key_points": [
            "理解状态、动作、奖励的基本概念",
            "知道试错学习与长期收益优化思路",
            "认识强化学习的典型应用场景",
        ],
        "text_material": "强化学习与监督学习不同，它更像是在不断试错中学习决策策略。学习这一节点有助于理解博弈、路径规划和智能控制类任务。",
        "image_url": "/materials/process-logic.svg",
        "video_title": "推荐检索词：强化学习 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "强化学习案例检索", "url": "https://search.bilibili.com/all?keyword=%E5%BC%BA%E5%8C%96%E5%AD%A6%E4%B9%A0%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "强化学习最核心的反馈信号通常是什么？",
                "options": ["奖励", "屏幕分辨率", "数据库主键", "页面布局"],
                "answer_index": 0,
                "explanation": "强化学习通过奖励信号来指导策略优化。",
            },
            {
                "question": "强化学习中的智能体主要在做什么？",
                "options": ["在环境中选择动作并根据反馈调整策略", "只读取静态文档", "只做图片压缩", "只导出报表"],
                "answer_index": 0,
                "explanation": "强化学习强调在交互环境中不断试错并改进决策。",
            },
        ],
    },
    {
        "slug": "foundation-models",
        "name": "大模型基础",
        "description": "理解大模型的参数规模、预训练机制、上下文能力与典型局限。",
        "category": "算法模型",
        "difficulty": 4,
        "estimated_minutes": 40,
        "key_points": [
            "认识预训练与微调的基本区别",
            "理解上下文窗口和参数规模的意义",
            "知道大模型能力与局限并存",
        ],
        "text_material": "大模型基础帮助学生把生成式应用和底层原理连起来理解，知道模型为什么能生成、为什么会出错，以及为什么提示方式会影响结果。",
        "image_url": "/materials/generative-workflow.svg",
        "video_title": "推荐检索词：大模型 基础",
        "video_url": "https://search.bilibili.com/all?keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B%20%E5%9F%BA%E7%A1%80",
        "resource_links": [
            {"label": "预训练与微调入门", "url": "https://search.bilibili.com/all?keyword=%E9%A2%84%E8%AE%AD%E7%BB%83%20%E5%BE%AE%E8%B0%83%20AI"},
        ],
        "quiz": [
            {
                "question": "大模型常见的能力来源之一是？",
                "options": ["大规模预训练", "只靠手工按钮", "只靠页面动画", "不需要任何数据"],
                "answer_index": 0,
                "explanation": "大规模预训练是大模型形成通用能力的重要基础。",
            },
            {
                "question": "为什么学习大模型基础有助于提升提示词使用效果？",
                "options": ["因为能更理解上下文和能力边界", "因为会自动获得管理员权限", "因为界面会更大", "因为不再需要验证答案"],
                "answer_index": 0,
                "explanation": "理解模型机制后，更容易设计合适的提示和验证流程。",
            },
        ],
    },
    {
        "slug": "ai-hallucination",
        "name": "AI幻觉与事实核验",
        "description": "认识生成式模型可能出现的幻觉问题，并掌握事实核验与来源比对的方法。",
        "category": "伦理素养",
        "difficulty": 3,
        "estimated_minutes": 30,
        "key_points": [
            "理解 AI 幻觉的常见表现",
            "掌握事实核验与多源比对方法",
            "形成“先验证再使用”的习惯",
        ],
        "text_material": "生成式 AI 可能给出看似流畅但并不准确的内容。学习这一节点的重点不是害怕使用 AI，而是学会验证、追溯与校正。",
        "image_url": "/materials/ethics-balance.svg",
        "video_title": "推荐检索词：AI 幻觉 事实核验",
        "video_url": "https://search.bilibili.com/all?keyword=AI%20%E5%B9%BB%E8%A7%89%20%E4%BA%8B%E5%AE%9E%E6%A0%B8%E9%AA%8C",
        "resource_links": [
            {"label": "事实核验方法检索", "url": "https://search.bilibili.com/all?keyword=%E4%BA%8B%E5%AE%9E%E6%A0%B8%E9%AA%8C%20AI"},
        ],
        "quiz": [
            {
                "question": "面对模型输出的专业结论，第一步更合理的做法是？",
                "options": ["核对来源并进行交叉验证", "立即直接引用", "删除全部记录", "默认绝对正确"],
                "answer_index": 0,
                "explanation": "事实核验强调来源检查和多源比对，而不是盲目信任。",
            },
            {
                "question": "AI 幻觉通常指什么现象？",
                "options": ["模型生成了貌似合理但不准确的信息", "电脑屏幕闪烁", "浏览器卡顿", "账号退出登录"],
                "answer_index": 0,
                "explanation": "AI 幻觉是生成式模型常见风险之一。",
            },
        ],
    },
    {
        "slug": "digital-copyright",
        "name": "数字版权与学术规范",
        "description": "学习版权、引用、署名和学术诚信的基本规则，规范使用 AI 生成内容。",
        "category": "伦理素养",
        "difficulty": 2,
        "estimated_minutes": 25,
        "key_points": [
            "理解版权和合理使用的边界",
            "掌握引用、署名和资料记录方式",
            "认识 AI 辅助创作中的学术诚信要求",
        ],
        "text_material": "在 AI 辅助写作和内容创作中，版权与学术规范格外重要。学生需要知道哪些内容能用、如何标注来源，以及如何说明 AI 的参与方式。",
        "image_url": "/materials/ethics-balance.svg",
        "video_title": "推荐检索词：数字版权 学术规范",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%95%B0%E5%AD%97%E7%89%88%E6%9D%83%20%E5%AD%A6%E6%9C%AF%E8%A7%84%E8%8C%83",
        "resource_links": [
            {"label": "学术规范案例检索", "url": "https://search.bilibili.com/all?keyword=%E5%AD%A6%E6%9C%AF%E8%A7%84%E8%8C%83%20AI"},
        ],
        "quiz": [
            {
                "question": "在使用 AI 辅助写作时，更符合学术规范的做法是？",
                "options": ["说明 AI 参与情况并核对引用来源", "直接当作完全原创提交", "删除引用信息", "隐藏全部资料出处"],
                "answer_index": 0,
                "explanation": "学术规范强调透明说明、正确引用和责任归属。",
            },
            {
                "question": "数字版权意识的核心之一是？",
                "options": ["尊重作品来源与使用边界", "默认互联网上的内容都可随意复制", "忽略作者署名", "只关注页面样式"],
                "answer_index": 0,
                "explanation": "版权意识要求在使用内容时关注授权与署名要求。",
            },
        ],
    },
    {
        "slug": "intelligent-agents",
        "name": "智能代理基础",
        "description": "理解智能代理如何围绕目标拆分任务、调用工具并持续迭代执行。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "认识智能代理的目标驱动特征",
            "理解规划、执行、反馈的基本流程",
            "知道代理系统需要人类设定边界和监督",
        ],
        "text_material": "智能代理是当前 AI 应用从“单次回答”走向“连续完成任务”的重要形态。学习这一节点有助于理解为什么任务拆分、工具调用和过程监督很重要。",
        "image_url": "/materials/process-logic.svg",
        "video_title": "推荐检索词：智能代理 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%99%BA%E8%83%BD%E4%BB%A3%E7%90%86%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "Agent 工作流案例检索", "url": "https://search.bilibili.com/all?keyword=AI%20Agent%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "智能代理与普通单轮问答相比，更强调什么？",
                "options": ["围绕目标连续规划和执行任务", "只输出一句话", "只会播放视频", "只做静态展示"],
                "answer_index": 0,
                "explanation": "代理系统更强调任务链路、步骤规划和结果反馈。",
            },
            {
                "question": "为什么智能代理仍然需要人的监督？",
                "options": ["因为任务边界、工具调用和结果质量都需要把关", "因为界面颜色不统一", "因为不能联网", "因为图谱没有节点"],
                "answer_index": 0,
                "explanation": "代理系统能力更强，但风险和边界控制同样更重要。",
            },
        ],
    },
    {
        "slug": "educational-data-analysis",
        "name": "教育数据分析",
        "description": "学习如何从学习行为、测验结果和问答互动中提取有效教学信息。",
        "category": "应用实践",
        "difficulty": 3,
        "estimated_minutes": 35,
        "key_points": [
            "理解学习行为数据的基本类型",
            "学会从数据中发现学习问题与教学机会",
            "关注教育数据使用中的隐私边界",
        ],
        "text_material": "教育数据分析把课程平台中的状态记录、自测成绩和提问行为串联起来，帮助教师和学生更准确地判断薄弱点和改进方向。",
        "image_url": "/materials/data-cycle.svg",
        "video_title": "推荐检索词：教育数据分析 入门",
        "video_url": "https://search.bilibili.com/all?keyword=%E6%95%99%E8%82%B2%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%20%E5%85%A5%E9%97%A8",
        "resource_links": [
            {"label": "学习分析案例检索", "url": "https://search.bilibili.com/all?keyword=%E5%AD%A6%E4%B9%A0%E5%88%86%E6%9E%90%20%E6%A1%88%E4%BE%8B"},
        ],
        "quiz": [
            {
                "question": "教育数据分析更适合帮助完成什么任务？",
                "options": ["发现班级共性薄弱点和学习趋势", "只换头像", "只下载视频", "只修改页面字体"],
                "answer_index": 0,
                "explanation": "教育数据分析的价值在于把行为数据转化为教学决策线索。",
            },
            {
                "question": "使用学习行为数据时仍应关注什么？",
                "options": ["隐私保护和数据使用边界", "只关注图表颜色", "忽略授权", "删除全部说明"],
                "answer_index": 0,
                "explanation": "教育场景中的数据分析同样要遵守隐私和合规要求。",
            },
        ],
    },
    {
        "slug": "ai-product-evaluation",
        "name": "AI产品体验评估",
        "description": "从准确性、可用性、交互反馈和风险提示等方面评估 AI 工具与产品表现。",
        "category": "应用实践",
        "difficulty": 2,
        "estimated_minutes": 30,
        "key_points": [
            "理解功能体验与结果质量要一起评估",
            "关注反馈效率、解释性和错误恢复体验",
            "学会形成结构化评估意见",
        ],
        "text_material": "AI 产品体验评估帮助学生不只会用工具，还能从学习者视角判断一个 AI 产品是否真正好用、可靠、清晰和安全。",
        "image_url": "/materials/evaluation-matrix.svg",
        "video_title": "推荐检索词：AI 产品体验评估",
        "video_url": "https://search.bilibili.com/all?keyword=AI%20%E4%BA%A7%E5%93%81%20%E4%BD%93%E9%AA%8C%E8%AF%84%E4%BC%B0",
        "resource_links": [
            {"label": "产品评测方法检索", "url": "https://search.bilibili.com/all?keyword=%E4%BA%A7%E5%93%81%E8%AF%84%E6%B5%8B%20AI"},
        ],
        "quiz": [
            {
                "question": "评估 AI 产品时，下列哪项更完整？",
                "options": ["同时看结果质量、交互体验和风险提示", "只看界面颜色", "只看是否能登录", "只看广告数量"],
                "answer_index": 0,
                "explanation": "完整评估需要兼顾准确性、体验和风险边界。",
            },
            {
                "question": "为什么学生也需要具备 AI 产品体验评估意识？",
                "options": ["因为会用还不够，还要会判断工具是否适合学习任务", "因为这样页面会更长", "因为可以跳过自测", "因为可以不再验证信息"],
                "answer_index": 0,
                "explanation": "具备评估意识后，学生能更理性地选择和使用 AI 工具。",
            },
        ],
    },
]

CATALOG_RELATIONS = [
    ("人工智能基础", "算法思维", "RELATED_TO"),
    ("人工智能基础", "机器学习", "PREREQUISITE_OF"),
    ("算法思维", "机器学习", "PREREQUISITE_OF"),
    ("数据素养", "数据采集与清洗", "PREREQUISITE_OF"),
    ("数据素养", "信息甄别与数字安全", "RELATED_TO"),
    ("数据采集与清洗", "机器学习", "PREREQUISITE_OF"),
    ("机器学习", "监督学习", "PREREQUISITE_OF"),
    ("机器学习", "无监督学习", "PREREQUISITE_OF"),
    ("监督学习", "模型评估", "PREREQUISITE_OF"),
    ("无监督学习", "模型评估", "PREREQUISITE_OF"),
    ("人工智能基础", "AI伦理与治理", "RELATED_TO"),
    ("AI伦理与治理", "生成式AI应用", "RELATED_TO"),
    ("提示词设计", "生成式AI应用", "PREREQUISITE_OF"),
    ("生成式AI应用", "人机协同实践", "PREREQUISITE_OF"),
    ("模型评估", "人机协同实践", "RELATED_TO"),
    ("信息甄别与数字安全", "生成式AI应用", "PREREQUISITE_OF"),
    ("机器学习", "神经网络基础", "PREREQUISITE_OF"),
    ("神经网络基础", "计算机视觉", "PREREQUISITE_OF"),
    ("神经网络基础", "自然语言处理", "PREREQUISITE_OF"),
    ("自然语言处理", "生成式AI应用", "PREREQUISITE_OF"),
    ("计算机视觉", "多模态AI", "RELATED_TO"),
    ("生成式AI应用", "多模态AI", "PREREQUISITE_OF"),
    ("人机协同实践", "AI项目式学习", "PREREQUISITE_OF"),
    ("模型评估", "AI项目式学习", "RELATED_TO"),
    ("人工智能基础", "知识表示与推理", "RELATED_TO"),
    ("算法思维", "知识表示与推理", "PREREQUISITE_OF"),
    ("数据素养", "开源数据集检索", "PREREQUISITE_OF"),
    ("开源数据集检索", "数据采集与清洗", "PREREQUISITE_OF"),
    ("数据采集与清洗", "特征工程", "PREREQUISITE_OF"),
    ("特征工程", "监督学习", "PREREQUISITE_OF"),
    ("机器学习", "强化学习", "PREREQUISITE_OF"),
    ("神经网络基础", "大模型基础", "PREREQUISITE_OF"),
    ("自然语言处理", "大模型基础", "PREREQUISITE_OF"),
    ("大模型基础", "生成式AI应用", "PREREQUISITE_OF"),
    ("信息甄别与数字安全", "AI幻觉与事实核验", "PREREQUISITE_OF"),
    ("生成式AI应用", "AI幻觉与事实核验", "RELATED_TO"),
    ("AI伦理与治理", "数字版权与学术规范", "PREREQUISITE_OF"),
    ("生成式AI应用", "智能代理基础", "PREREQUISITE_OF"),
    ("大模型基础", "智能代理基础", "PREREQUISITE_OF"),
    ("数据素养", "教育数据分析", "PREREQUISITE_OF"),
    ("模型评估", "AI产品体验评估", "PREREQUISITE_OF"),
    ("教育数据分析", "AI产品体验评估", "RELATED_TO"),
    ("AI幻觉与事实核验", "人机协同实践", "RELATED_TO"),
    ("智能代理基础", "AI项目式学习", "RELATED_TO"),
    ("数字版权与学术规范", "AI项目式学习", "RELATED_TO"),
    ("AI产品体验评估", "AI项目式学习", "RELATED_TO"),
]


CATEGORY_ENRICHMENTS = {
    "基础概念": {
        "study_tips": [
            "先用自己的话复述概念，再对照课程定义检查是否遗漏关键边界。",
            "把当前节点与图谱中的前置知识、后续知识连起来看，避免孤立记忆。",
        ],
        "common_mistakes": [
            "只背术语，不结合真实学习场景理解概念作用。",
            "忽略节点之间的依赖关系，导致后续知识点理解断层。",
        ],
        "practice_template": "请围绕“{name}”整理一张 3 栏学习卡：概念定义、生活中的例子、它与其他知识点的关系。",
    },
    "数字素养": {
        "study_tips": [
            "学习时同时关注方法流程和风险意识，尤其是数据来源与使用边界。",
            "尝试把当前知识点应用到信息检索、数据处理或安全判断的具体案例中。",
        ],
        "common_mistakes": [
            "把工具熟练度等同于数字素养，忽视判断与验证环节。",
            "只看结果，不追溯数据来源、采集方式和隐私影响。",
        ],
        "practice_template": "请结合“{name}”完成一次微任务：选取一个真实案例，写出操作步骤、风险点和你的判断依据。",
    },
    "算法模型": {
        "study_tips": [
            "先抓住任务类型、输入输出和评价方式，再进入模型细节。",
            "遇到抽象概念时，用图示或表格把训练流程拆成几个固定环节。",
        ],
        "common_mistakes": [
            "只记模型名称，不区分它解决的任务和适用条件。",
            "忽视评估指标和数据质量，误以为模型效果只和算法复杂度有关。",
        ],
        "practice_template": "请围绕“{name}”设计一个最小实验：写清输入、输出、训练思路，以及你会如何判断结果是否可靠。",
    },
    "伦理素养": {
        "study_tips": [
            "把伦理议题放到具体应用场景中讨论，思考谁会受影响、由谁负责。",
            "遇到“公平”“安全”“透明”这类概念时，尽量给出可操作的判断标准。",
        ],
        "common_mistakes": [
            "把伦理当作附加内容，没有与模型设计和使用流程联动考虑。",
            "只停留在价值判断层面，没有提出可执行的治理措施。",
        ],
        "practice_template": "请围绕“{name}”写一个课堂情境分析：问题是什么、风险在哪里、可以采取哪些治理措施。",
    },
    "应用实践": {
        "study_tips": [
            "先明确任务目标和输出形式，再决定如何调用模型或组合工具。",
            "把每次尝试记录下来，比较不同提示、材料或流程带来的结果差异。",
        ],
        "common_mistakes": [
            "一开始就追求最终答案，忽视中间验证和迭代修改。",
            "只会操作工具，不总结为什么这样做有效。",
        ],
        "practice_template": "请围绕“{name}”完成一次课堂演练：说明目标、操作步骤、结果截图或记录，以及你的复盘结论。",
    },
}


SLUG_ENRICHMENTS = {
    "ai-basics": {
        "study_tips": [
            "把人工智能拆成感知、判断、生成三类能力，再分别寻找对应案例。",
        ],
        "common_mistakes": [
            "把 AI 简化成某一个单独产品，而没有看到背后的能力结构。",
        ],
    },
    "data-literacy": {
        "study_tips": [
            "练习从“数据从哪里来、有什么偏差、能否直接用于判断”这三个问题切入。",
        ],
        "practice_task": "选取一个你最近接触的数据或图表，判断其来源是否可靠、是否可能有偏差，并给出解释。",
    },
    "machine-learning": {
        "study_tips": [
            "用“数据 - 特征 - 训练 - 评估”四步框架梳理机器学习的基本流程。",
        ],
        "practice_task": "画出一个机器学习流程图，并为每一步写一句解释，说明它在整体系统中的作用。",
    },
    "model-evaluation": {
        "practice_task": "比较两个假想模型的准确率与召回率，说明在教育场景里你会更倾向选择哪一个以及原因。",
    },
    "prompt-design": {
        "practice_task": "以“请帮我规划一次 AI 课程复习”为主题，分别写出一个低质量提示词和一个高质量提示词，并比较输出差异。",
    },
    "generative-ai": {
        "common_mistakes": [
            "把生成式 AI 当作标准答案机器，而不是学习辅助工具。",
        ],
        "practice_task": "使用同一主题连续设计两轮提示词，比较模型输出，并记录你是如何通过补充约束让结果更贴合任务的。",
    },
    "human-ai-collaboration": {
        "practice_task": "围绕一次作业或项目任务，标出哪些环节由你主导，哪些环节由 AI 提供辅助，并写出你的质量把关方式。",
    },
    "ai-project-learning": {
        "practice_task": "为你的毕设或课堂项目写一页项目蓝图：目标、关键节点、所需资料、验证方式和最终展示形式。",
    },
}


def _merge_unique_items(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for item in group:
            if item and item not in merged:
                merged.append(item)
    return merged


def _build_quiz_bank(item: dict, study_tips: list[str], common_mistakes: list[str], practice_task: str) -> list[dict]:
    existing_quiz = list(item.get("quiz", []))
    category = item.get("category", "知识图谱")
    key_points = item.get("key_points", [])
    name = item["name"]
    description = item.get("description") or f"{name} 是课程中的重要知识点。"

    generated_questions = [
        {
            "question": f"【判断题】学习“{name}”时，只记住结论，不理解它与前后置知识点的关系也足够。",
            "options": ["正确", "错误"],
            "answer_index": 1,
            "explanation": "知识图谱学习强调结构化理解，节点关系与节点内容同样重要。",
        },
        {
            "question": f"【判断题】“{name}”属于“{category}”这一学习主题。",
            "options": ["正确", "错误"],
            "answer_index": 0,
            "explanation": f"{name} 在课程图谱中被归入“{category}”类别，便于分主题学习。",
        },
        {
            "question": f"【判断题】面对“{name}”的学习任务，先看材料再做自测通常比直接答题更有效。",
            "options": ["正确", "错误"],
            "answer_index": 0,
            "explanation": "先完成知识梳理和材料阅读，再做自测，更容易形成稳定理解。",
        },
        {
            "question": f"下列哪一项最能概括“{name}”在课程中的学习目标？",
            "options": [
                description,
                "仅用于记忆课程术语，不涉及应用场景",
                "只和登录注册功能有关，与图谱学习无关",
                "它的作用只是增加页面中的节点数量",
            ],
            "answer_index": 0,
            "explanation": "题干中的课程描述对应了该知识点的核心学习目标。",
        },
        {
            "question": f"关于“{name}”的学习重点，下列哪一项更合理？",
            "options": [
                key_points[0] if key_points else f"理解 {name} 的核心作用和适用场景",
                "跳过前置知识点，直接记住答案",
                "只记视频标题，不做任何整理",
                "仅凭一次自测结果判断是否完全掌握",
            ],
            "answer_index": 0,
            "explanation": "学习重点应回到节点本身的核心要点，而不是停留在表面操作。",
        },
        {
            "question": f"如果你准备继续深入“{name}”，下列哪种做法最符合图谱学习逻辑？",
            "options": [
                study_tips[0] if study_tips else f"先梳理 {name} 的核心要点，再结合节点关系继续学习",
                "忽略图谱关系，随机切换到任意节点",
                "不看材料直接把状态改为已掌握",
                "只收藏答案，不做任何理解",
            ],
            "answer_index": 0,
            "explanation": "图谱导学的核心是先理解节点，再结合依赖关系组织学习顺序。",
        },
        {
            "question": f"围绕“{name}”的实践任务中，更值得优先完成的是哪一项？",
            "options": [
                practice_task,
                "只截一张页面图，不记录思路",
                "复制别人的结论，不做自己的分析",
                "跳过实践任务，直接结束本节点学习",
            ],
            "answer_index": 0,
            "explanation": "实践任务的价值在于把概念转化为自己的分析和操作过程。",
        },
        {
            "question": f"【判断题】“{name}”的常见误区之一，是只关注结果而忽视学习过程与判断依据。",
            "options": ["正确", "错误"],
            "answer_index": 0,
            "explanation": common_mistakes[0] if common_mistakes else "很多节点都强调不能只看结果，还要理解过程和判断依据。",
        },
        {
            "question": f"当你在“{name}”上遇到困难时，更推荐的求助方式是？",
            "options": [
                "在当前节点下结合具体困惑向教师提问，并说明自己已尝试的方法",
                "什么都不写，只说“我不会”",
                "直接跳到完全无关的节点",
                "删除学习记录，重新开始",
            ],
            "answer_index": 0,
            "explanation": "高质量提问应结合具体节点、问题背景和已尝试的方法，便于教师针对性指导。",
        },
        {
            "question": f"对于“{name}”的学习结果，下列哪种完成标准更合理？",
            "options": [
                "能解释概念、找到材料、完成自测，并说明它与其他节点的关系",
                "只记住一个关键词即可",
                "只要点开过页面就算掌握",
                "只收藏教师回答，不做任何复盘",
            ],
            "answer_index": 0,
            "explanation": "一个知识点的掌握应体现为理解、应用、验证和关系串联，而不只是浏览过页面。",
        },
    ]

    merged_quiz: list[dict] = []
    seen_questions: set[str] = set()
    for question in existing_quiz + generated_questions:
        title = question["question"]
        if title in seen_questions:
            continue
        merged_quiz.append(question)
        seen_questions.add(title)
        if len(merged_quiz) >= 10:
            break
    return merged_quiz


def _build_enriched_catalog_concepts() -> list[dict]:
    concepts: list[dict] = []
    for item in CATALOG_CONCEPTS:
        category_defaults = CATEGORY_ENRICHMENTS.get(item.get("category"), {})
        slug_defaults = SLUG_ENRICHMENTS.get(item["slug"], {})
        key_points = item.get("key_points", [])
        study_tips = _merge_unique_items(
            key_points[:2],
            category_defaults.get("study_tips", []),
            slug_defaults.get("study_tips", []),
        )
        common_mistakes = _merge_unique_items(
            category_defaults.get("common_mistakes", []),
            slug_defaults.get("common_mistakes", []),
        )
        practice_task = (
            slug_defaults.get("practice_task")
            or category_defaults.get("practice_template", "请围绕“{name}”完成一项学习实践，并记录你的过程、结果和反思。").format(name=item["name"])
        )
        quiz = _build_quiz_bank(item, study_tips[:4], common_mistakes[:3], practice_task)

        concepts.append(
            {
                **item,
                "study_tips": study_tips[:4],
                "common_mistakes": common_mistakes[:3],
                "practice_task": practice_task,
                "quiz": quiz,
            }
        )
    return concepts


def get_graph_catalog() -> tuple[list[dict], list[tuple[str, str, str]]]:
    return _build_enriched_catalog_concepts(), CATALOG_RELATIONS
