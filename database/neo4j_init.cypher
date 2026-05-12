MERGE (ai:Concept {
  name: "人工智能基础",
  description: "理解人工智能的定义、发展与典型应用场景。",
  category: "基础概念",
  difficulty: 1
})
MERGE (data:Concept {
  name: "数据素养",
  description: "了解数据获取、清洗、分析与隐私保护。",
  category: "数字素养",
  difficulty: 2
})
MERGE (ml:Concept {
  name: "机器学习",
  description: "掌握监督学习、无监督学习与常见模型。",
  category: "算法模型",
  difficulty: 3
})
MERGE (ethics:Concept {
  name: "AI伦理与治理",
  description: "认识算法偏见、透明性、责任与治理框架。",
  category: "伦理素养",
  difficulty: 2
})
MERGE (prompt:Concept {
  name: "生成式AI应用",
  description: "理解大模型使用、提示词设计与风险控制。",
  category: "应用实践",
  difficulty: 3
})
MERGE (algorithm:Concept {
  name: "算法思维",
  description: "从任务拆解、流程设计与规则表达角度理解算法思维。",
  category: "基础概念",
  difficulty: 1
})
MERGE (cleaning:Concept {
  name: "数据采集与清洗",
  description: "掌握数据采集、异常值处理、缺失值处理与格式统一。",
  category: "数字素养",
  difficulty: 2
})
MERGE (supervised:Concept {
  name: "监督学习",
  description: "理解分类与回归任务，以及标签在训练中的作用。",
  category: "算法模型",
  difficulty: 3
})
MERGE (unsupervised:Concept {
  name: "无监督学习",
  description: "理解聚类、降维等无标签学习方式。",
  category: "算法模型",
  difficulty: 3
})
MERGE (evaluation:Concept {
  name: "模型评估",
  description: "通过准确率、召回率与泛化能力分析模型效果。",
  category: "算法模型",
  difficulty: 3
})
MERGE (safety:Concept {
  name: "信息甄别与数字安全",
  description: "提升信息辨识、账号安全与隐私保护能力。",
  category: "数字素养",
  difficulty: 2
})
MERGE (promptDesign:Concept {
  name: "提示词设计",
  description: "掌握目标明确、结构清晰、上下文充分的提示词构建方法。",
  category: "应用实践",
  difficulty: 2
})
MERGE (collab:Concept {
  name: "人机协同实践",
  description: "通过案例任务理解人机协同分工、验证与优化流程。",
  category: "应用实践",
  difficulty: 2
})
MERGE (neural:Concept {
  name: "神经网络基础",
  description: "了解神经网络层、激活函数与特征提取的基本机制。",
  category: "算法模型",
  difficulty: 4
})
MERGE (vision:Concept {
  name: "计算机视觉",
  description: "理解图像分类、目标检测等视觉任务及其教育应用。",
  category: "应用实践",
  difficulty: 3
})
MERGE (nlp:Concept {
  name: "自然语言处理",
  description: "理解文本分类、问答、摘要与对话系统的基本思路。",
  category: "应用实践",
  difficulty: 3
})
MERGE (multimodal:Concept {
  name: "多模态AI",
  description: "认识图文音等多种模态联合理解与生成的场景。",
  category: "应用实践",
  difficulty: 4
})
MERGE (project:Concept {
  name: "AI项目式学习",
  description: "围绕真实任务完成选题、设计、实现展示与复盘。",
  category: "应用实践",
  difficulty: 3
})
MERGE (knowledge:Concept {
  name: "知识表示与推理",
  description: "理解知识如何被结构化表示，并通过规则完成推理判断。",
  category: "算法模型",
  difficulty: 3
})
MERGE (dataset:Concept {
  name: "开源数据集检索",
  description: "学习如何检索公开数据集，并判断其来源、质量与授权方式。",
  category: "数字素养",
  difficulty: 2
})
MERGE (feature:Concept {
  name: "特征工程",
  description: "理解特征选择、构造与变换对模型效果的影响。",
  category: "算法模型",
  difficulty: 3
})
MERGE (reinforcement:Concept {
  name: "强化学习",
  description: "理解智能体如何通过奖励信号在环境中优化行为策略。",
  category: "算法模型",
  difficulty: 4
})
MERGE (foundation:Concept {
  name: "大模型基础",
  description: "理解大模型的预训练机制、上下文能力与典型局限。",
  category: "算法模型",
  difficulty: 4
})
MERGE (hallucination:Concept {
  name: "AI幻觉与事实核验",
  description: "认识生成式模型的幻觉现象，并掌握事实核验方法。",
  category: "伦理素养",
  difficulty: 3
})
MERGE (copyright:Concept {
  name: "数字版权与学术规范",
  description: "学习版权、引用和学术诚信规则，规范使用 AI 生成内容。",
  category: "伦理素养",
  difficulty: 2
})
MERGE (agent:Concept {
  name: "智能代理基础",
  description: "理解智能代理如何拆解目标、调用工具并持续迭代执行。",
  category: "应用实践",
  difficulty: 3
})
MERGE (eduData:Concept {
  name: "教育数据分析",
  description: "从学习行为、自测成绩和问答互动中提取有效教学信息。",
  category: "应用实践",
  difficulty: 3
})
MERGE (productEval:Concept {
  name: "AI产品体验评估",
  description: "从准确性、可用性和风险提示等方面评估 AI 工具表现。",
  category: "应用实践",
  difficulty: 2
})

MERGE (ai)-[:PREREQUISITE_OF]->(ml)
MERGE (ai)-[:RELATED_TO]->(algorithm)
MERGE (data)-[:PREREQUISITE_OF]->(ml)
MERGE (data)-[:PREREQUISITE_OF]->(cleaning)
MERGE (cleaning)-[:PREREQUISITE_OF]->(ml)
MERGE (algorithm)-[:PREREQUISITE_OF]->(ml)
MERGE (ml)-[:PREREQUISITE_OF]->(supervised)
MERGE (ml)-[:PREREQUISITE_OF]->(unsupervised)
MERGE (supervised)-[:PREREQUISITE_OF]->(evaluation)
MERGE (unsupervised)-[:PREREQUISITE_OF]->(evaluation)
MERGE (ml)-[:PREREQUISITE_OF]->(prompt)
MERGE (ethics)-[:RELATED_TO]->(prompt)
MERGE (data)-[:RELATED_TO]->(ethics)
MERGE (data)-[:RELATED_TO]->(safety)
MERGE (safety)-[:PREREQUISITE_OF]->(prompt)
MERGE (promptDesign)-[:PREREQUISITE_OF]->(prompt)
MERGE (prompt)-[:PREREQUISITE_OF]->(collab)
MERGE (evaluation)-[:RELATED_TO]->(collab)
MERGE (ml)-[:PREREQUISITE_OF]->(neural)
MERGE (neural)-[:PREREQUISITE_OF]->(vision)
MERGE (neural)-[:PREREQUISITE_OF]->(nlp)
MERGE (nlp)-[:PREREQUISITE_OF]->(prompt)
MERGE (vision)-[:RELATED_TO]->(multimodal)
MERGE (prompt)-[:PREREQUISITE_OF]->(multimodal)
MERGE (collab)-[:PREREQUISITE_OF]->(project)
MERGE (evaluation)-[:RELATED_TO]->(project)
MERGE (ai)-[:RELATED_TO]->(knowledge)
MERGE (algorithm)-[:PREREQUISITE_OF]->(knowledge)
MERGE (data)-[:PREREQUISITE_OF]->(dataset)
MERGE (dataset)-[:PREREQUISITE_OF]->(cleaning)
MERGE (cleaning)-[:PREREQUISITE_OF]->(feature)
MERGE (feature)-[:PREREQUISITE_OF]->(supervised)
MERGE (ml)-[:PREREQUISITE_OF]->(reinforcement)
MERGE (neural)-[:PREREQUISITE_OF]->(foundation)
MERGE (nlp)-[:PREREQUISITE_OF]->(foundation)
MERGE (foundation)-[:PREREQUISITE_OF]->(prompt)
MERGE (safety)-[:PREREQUISITE_OF]->(hallucination)
MERGE (prompt)-[:RELATED_TO]->(hallucination)
MERGE (ethics)-[:PREREQUISITE_OF]->(copyright)
MERGE (prompt)-[:PREREQUISITE_OF]->(agent)
MERGE (foundation)-[:PREREQUISITE_OF]->(agent)
MERGE (data)-[:PREREQUISITE_OF]->(eduData)
MERGE (evaluation)-[:PREREQUISITE_OF]->(productEval)
MERGE (eduData)-[:RELATED_TO]->(productEval)
MERGE (hallucination)-[:RELATED_TO]->(collab)
MERGE (agent)-[:RELATED_TO]->(project)
MERGE (copyright)-[:RELATED_TO]->(project)
MERGE (productEval)-[:RELATED_TO]->(project);
