"""
AI 服务层 - 高级 AI 功能封装

功能：
  1. AI 自动出题：从课程资料/文本自动生成题目入题库
  2. AI 自动批改简答题
  3. AI 生成课程摘要
  4. AI 生成 PPT 大纲
"""
import json
import re

from .client import LLMClient, LLMError


class AIService:
    """AI 服务统一入口"""

    def __init__(self, user=None):
        self.user = user
        self.client = LLMClient()

    # ==================== AI 自动出题 ====================

    def generate_questions(self, content, question_type='single_choice',
                           count=5, difficulty='medium', tags=''):
        """
        从文本内容自动生成题目

        :param content: 课程资料文本（最多 8000 字）
        :param question_type: 题目类型
        :param count: 生成数量（1-20）
        :param difficulty: 难度 easy/medium/hard
        :param tags: 标签
        :return: dict with 'questions' list and 'error' str
        """
        content = content[:8000]
        count = max(1, min(20, count))

        type_map = {
            'single_choice': '单选题（4个选项A/B/C/D，1个正确答案）',
            'multi_choice': '多选题（4个选项A/B/C/D，2-4个正确答案）',
            'true_false': '判断题（答案为 True 或 False）',
            'fill_blank': '填空题（答案为填空内容）',
            'essay': '简答题（参考答案为要点列表）',
        }
        diff_map = {
            'easy': '简单（基础知识回忆）',
            'medium': '中等（理解和应用）',
            'hard': '困难（分析和综合评价）',
        }

        system_prompt = f"""你是一位专业的培训考试出题专家。请根据用户提供的学习材料，生成{count}道{type_map.get(question_type, '单选题')}。
难度要求：{diff_map.get(difficulty, '中等')}。

输出要求：严格使用 JSON 数组格式，每个题目包含以下字段：
- question_text: 题目内容
- option_a, option_b, option_c, option_d: 选项内容（判断题和填空题留空）
- correct_answer: 正确答案（单选题填A/B/C/D，多选题填如"A,B"，判断题填True/False，填空题填答案文本，简答题填参考答案）
- analysis: 答案解析（简要说明为什么是这个答案）

只输出JSON数组，不要输出其他任何文字。示例格式：
[{{"question_text":"示例题目？","option_a":"选项A","option_b":"选项B","option_c":"选项C","option_d":"选项D","correct_answer":"A","analysis":"解析说明"}}]"""

        user_prompt = f'请根据以下学习材料生成题目：\n\n{content}'

        try:
            response = self.client.chat_with_system(
                system_prompt, user_prompt,
                task_type='generate_questions',
                user=self.user,
                input_text=content,
                temperature=0.8,
            )

            # 解析 JSON
            questions = self._parse_json_response(response)

            return {'questions': questions, 'error': None}

        except LLMError as e:
            return {'questions': [], 'error': str(e)}
        except Exception as e:
            return {'questions': [], 'error': f'解析失败: {str(e)}'}

    # ==================== AI 自动批改 ====================

    def grade_essay(self, question_text, reference_answer, student_answer, max_score=10):
        """
        AI 批改简答题

        :return: dict with 'score', 'comment', 'error'
        """
        system_prompt = f"""你是一位严格的阅卷老师。请根据题目和参考答案，对学生的回答进行评分。

评分规则：
- 满分 {max_score} 分
- 根据答案的准确性、完整性、逻辑性综合评分
- 关键知识点命中率高给高分
- 语义相近但表述不同可给部分分数

输出要求：严格使用 JSON 格式：
{{"score": 分数, "comment": "评语（说明扣分原因）"}}

只输出JSON，不要其他文字。"""

        user_prompt = f"""题目：{question_text}

参考答案：{reference_answer}

学生回答：{student_answer}"""

        try:
            response = self.client.chat_with_system(
                system_prompt, user_prompt,
                task_type='grade_essay',
                user=self.user,
                input_text=user_prompt,
                temperature=0.3,
            )

            result = self._parse_json_response(response)
            if isinstance(result, list) and result:
                result = result[0]
            if isinstance(result, dict):
                return {
                    'score': min(int(result.get('score', 0)), max_score),
                    'comment': result.get('comment', ''),
                    'error': None,
                }

            return {'score': 0, 'comment': '', 'error': 'AI返回格式异常'}

        except LLMError as e:
            return {'score': 0, 'comment': '', 'error': str(e)}

    # ==================== AI 课程摘要 ====================

    def summarize_course(self, course_title, course_description, materials_info):
        """
        生成课程摘要

        :param materials_info: 资料列表 [{"title": "...", "type": "...", "description": "..."}]
        :return: dict with 'summary', 'error'
        """
        materials_text = '\n'.join(
            f'- [{m.get("type", "")}] {m.get("title", "")}: {m.get("description", "")}'
            for m in materials_info
        )

        system_prompt = """你是一位培训课程设计师。请根据课程信息生成一份结构化的课程摘要。
输出格式：
1. 课程目标（1-2句话）
2. 学习要点（3-5个要点）
3. 适用对象（1句话）
4. 建议学习路径（简要说明）

使用简洁的中文输出。"""

        user_prompt = f"""课程标题：{course_title}
课程描述：{course_description}

课程资料：
{materials_text}"""

        try:
            response = self.client.chat_with_system(
                system_prompt, user_prompt,
                task_type='summarize',
                user=self.user,
                input_text=user_prompt,
                temperature=0.5,
            )
            return {'summary': response, 'error': None}

        except LLMError as e:
            return {'summary': '', 'error': str(e)}

    # ==================== AI PPT 大纲 ====================

    def generate_ppt_outline(self, course_title, course_description, materials_info):
        """
        生成 PPT 大纲

        :return: dict with 'outline', 'error'
        """
        materials_text = '\n'.join(
            f'- [{m.get("type", "")}] {m.get("title", "")}'
            for m in materials_info
        )

        system_prompt = """你是一位PPT设计专家。请根据课程信息生成一份PPT大纲。
输出要求：严格使用 JSON 数组格式，每页包含：
- title: 页面标题
- bullet_points: 要点列表（3-5个要点）
- layout: 布局类型（cover/content/section/closing）

只输出JSON数组，不要其他文字。"""

        user_prompt = f"""课程标题：{course_title}
课程描述：{course_description}

课程资料：
{materials_text}

请生成 8-15 页的PPT大纲。"""

        try:
            response = self.client.chat_with_system(
                system_prompt, user_prompt,
                task_type='ppt_outline',
                user=self.user,
                input_text=user_prompt,
                temperature=0.6,
            )
            outline = self._parse_json_response(response)
            return {'outline': outline, 'error': None}

        except LLMError as e:
            return {'outline': [], 'error': str(e)}

    # ==================== 辅助方法 ====================

    def _parse_json_response(self, text):
        """从 AI 回复中提取 JSON（兼容 markdown 代码块包裹）"""
        text = text.strip()

        # 去除 markdown 代码块标记
        if text.startswith('```'):
            lines = text.split('\n')
            # 去掉首行 ```json 或 ```
            lines = lines[1:]
            # 去掉末尾 ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取第一个 JSON 数组或对象
        patterns = [
            r'\[[\s\S]*\]',   # JSON 数组
            r'\{[\s\S]*\}',    # JSON 对象
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue

        raise ValueError(f'无法解析为JSON: {text[:200]}')