"""
大模型管理 - 视图
"""
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models

from apps.courses.models import Course
from apps.exams.models import Exam, ExamAttempt, Question, Answer

from .models import LLMProvider, AIUsageLog
from .services import AIService
from .client import LLMError


def is_admin(user):
    return user.is_staff or user.is_superuser


# ==================== 模型配置管理 ====================

@login_required
@user_passes_test(is_admin)
def provider_list_view(request):
    """模型配置列表"""
    providers = LLMProvider.objects.all()
    presets = LLMProvider.get_provider_presets()
    return render(request, 'llm/providers.html', {
        'providers': providers,
        'presets_json': json.dumps(presets),
    })


@login_required
@user_passes_test(is_admin)
def provider_create_view(request):
    """创建模型配置"""
    if request.method == 'POST':
        provider = LLMProvider.objects.create(
            name=request.POST.get('name', ''),
            provider=request.POST.get('provider', 'kimi'),
            api_key=request.POST.get('api_key', ''),
            base_url=request.POST.get('base_url', ''),
            model_name=request.POST.get('model_name', ''),
            temperature=float(request.POST.get('temperature', 0.7)),
            max_tokens=int(request.POST.get('max_tokens', 4096)),
            is_active=request.POST.get('is_active') == 'on',
            is_default=request.POST.get('is_default') == 'on',
        )
        messages.success(request, f'模型配置 "{provider.name}" 创建成功。')
        return redirect('llm:providers')

    presets = LLMProvider.get_provider_presets()
    return render(request, 'llm/provider_form.html', {
        'presets_json': json.dumps(presets),
        'provider_choices': LLMProvider.PROVIDER_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
def provider_edit_view(request, pk):
    """编辑模型配置"""
    provider = get_object_or_404(LLMProvider, pk=pk)
    if request.method == 'POST':
        provider.name = request.POST.get('name', '')
        provider.provider = request.POST.get('provider', 'kimi')
        provider.api_key = request.POST.get('api_key', '')
        provider.base_url = request.POST.get('base_url', '')
        provider.model_name = request.POST.get('model_name', '')
        provider.temperature = float(request.POST.get('temperature', 0.7))
        provider.max_tokens = int(request.POST.get('max_tokens', 4096))
        provider.is_active = request.POST.get('is_active') == 'on'
        provider.is_default = request.POST.get('is_default') == 'on'
        provider.save()
        messages.success(request, '模型配置已更新。')
        return redirect('llm:providers')

    presets = LLMProvider.get_provider_presets()
    return render(request, 'llm/provider_form.html', {
        'provider': provider,
        'presets_json': json.dumps(presets),
        'provider_choices': LLMProvider.PROVIDER_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def provider_delete_view(request, pk):
    """删除模型配置"""
    provider = get_object_or_404(LLMProvider, pk=pk)
    provider.delete()
    messages.success(request, '模型配置已删除。')
    return redirect('llm:providers')


@login_required
@user_passes_test(is_admin)
def provider_test_view(request, pk):
    """测试模型连通性"""
    provider = get_object_or_404(LLMProvider, pk=pk)
    try:
        from .client import LLMClient
        client = LLMClient(provider)
        result = client.chat_with_system(
            '你是一个测试助手。',
            '请回复"连接成功"四个字。',
            task_type='other',
            user=request.user,
        )
        return JsonResponse({'ok': True, 'message': result})
    except LLMError as e:
        return JsonResponse({'ok': False, 'message': str(e)})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': f'未知错误: {str(e)}'})


# ==================== AI 使用日志 ====================

@login_required
@user_passes_test(is_admin)
def usage_logs_view(request):
    """AI 调用日志"""
    logs = AIUsageLog.objects.select_related('provider', 'created_by').all()[:200]
    return render(request, 'llm/logs.html', {'logs': logs})


# ==================== AI 自动出题 ====================

@login_required
@user_passes_test(is_admin)
def ai_generate_questions_view(request):
    """AI 自动出题页面"""
    from apps.question_bank.models import QuestionBank, KnowledgePoint

    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        content = request.POST.get('content', '')
        question_type = request.POST.get('question_type', 'single_choice')
        count = int(request.POST.get('count', 5))
        difficulty = request.POST.get('difficulty', 'medium')
        tags = request.POST.get('tags', '')
        kp_ids = request.POST.getlist('knowledge_points')

        if not content:
            messages.error(request, '请输入学习材料内容。')
            return redirect('llm:ai_questions')

        try:
            service = AIService(user=request.user)
            result = service.generate_questions(
                content=content,
                question_type=question_type,
                count=count,
                difficulty=difficulty,
                tags=tags,
            )

            if result['error']:
                messages.error(request, f'AI出题失败：{result["error"]}')
                return redirect('llm:ai_questions')

            questions = result['questions']

            if action == 'save' and questions:
                # 保存到题库
                saved = 0
                for q in questions:
                    QuestionBank.objects.create(
                        question_text=q.get('question_text', ''),
                        question_type=question_type,
                        option_a=q.get('option_a', ''),
                        option_b=q.get('option_b', ''),
                        option_c=q.get('option_c', ''),
                        option_d=q.get('option_d', ''),
                        correct_answer=q.get('correct_answer', ''),
                        analysis=q.get('analysis', ''),
                        score=5,
                        difficulty=difficulty,
                        tags=tags,
                        created_by=request.user,
                    )
                    saved += 1
                messages.success(request, f'成功生成并保存 {saved} 道题目到题库！')
                return redirect('question_bank:list')

            # 预览模式
            return render(request, 'llm/ai_questions.html', {
                'generated_questions': questions,
                'content': content,
                'question_type': question_type,
                'count': count,
                'difficulty': difficulty,
                'tags': tags,
                'type_choices': QuestionBank.QUESTION_TYPE_CHOICES,
                'difficulty_choices': QuestionBank.DIFFICULTY_CHOICES,
                'knowledge_points': KnowledgePoint.objects.all(),
            })

        except LLMError as e:
            messages.error(request, f'AI服务不可用：{str(e)}')
            return redirect('llm:ai_questions')

    return render(request, 'llm/ai_questions.html', {
        'type_choices': QuestionBank.QUESTION_TYPE_CHOICES,
        'difficulty_choices': QuestionBank.DIFFICULTY_CHOICES,
        'knowledge_points': KnowledgePoint.objects.all(),
    })


# ==================== AI 自动批改 ====================

@login_required
@user_passes_test(is_admin)
def ai_grade_view(request, pk):
    """AI 批改简答题 - 考试成绩页面"""
    exam = get_object_or_404(Exam, pk=pk)

    # 获取需要批改的简答题答案
    essay_answers = Answer.objects.filter(
        question__exam=exam,
        question__question_type='essay',
        attempt__status='completed',
    ).select_related('question', 'attempt')

    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        action = request.POST.get('action', 'grade')

        answer = get_object_or_404(Answer, pk=answer_id)

        try:
            service = AIService(user=request.user)
            result = service.grade_essay(
                question_text=answer.question.question_text,
                reference_answer=answer.question.correct_answer,
                student_answer=answer.user_answer,
                max_score=answer.question.score,
            )

            if result['error']:
                return JsonResponse({'ok': False, 'message': result['error']})

            if action == 'apply':
                # 应用评分
                answer.score = result['score']
                answer.is_correct = result['score'] >= answer.question.score * 0.6
                answer.save()

                # 更新考试总分
                attempt = answer.attempt
                total = attempt.answers.aggregate(
                    total=models.Sum('score')
                )['total'] or 0
                attempt.score = total
                attempt.is_passed = total >= exam.pass_score
                attempt.save()

            return JsonResponse({
                'ok': True,
                'score': result['score'],
                'comment': result['comment'],
                'max_score': answer.question.score,
            })

        except LLMError as e:
            return JsonResponse({'ok': False, 'message': str(e)})

    return render(request, 'llm/ai_grade.html', {
        'exam': exam,
        'essay_answers': essay_answers,
    })


# ==================== AI 课程摘要 ====================

@login_required
def ai_course_summary_view(request, pk):
    """AI 生成课程摘要"""
    course = get_object_or_404(Course, pk=pk)
    materials = course.materials.all()

    materials_info = [
        {
            'title': m.title,
            'type': m.get_file_type_display(),
            'description': m.description or '',
        }
        for m in materials
    ]

    try:
        service = AIService(user=request.user)
        result = service.summarize_course(
            course_title=course.title,
            course_description=course.description or '',
            materials_info=materials_info,
        )

        if result['error']:
            return JsonResponse({'ok': False, 'message': result['error']})

        return JsonResponse({'ok': True, 'summary': result['summary']})

    except LLMError as e:
        return JsonResponse({'ok': False, 'message': str(e)})