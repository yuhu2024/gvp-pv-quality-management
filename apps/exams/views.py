"""
在线考试 - 视图
"""
import json
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from apps.courses.models import Course
from .models import Exam, ExamAttempt, Question, Answer, AnswerLog, PaperTemplate, PaperRule


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_staff or user.is_superuser


# 考试试卷上传安全配置
ALLOWED_EXAM_PAPER_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_EXAM_PAPER_SIZE = 20 * 1024 * 1024  # 20MB


def validate_exam_paper(file):
    """验证考试试卷文件"""
    if not file:
        return
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXAM_PAPER_EXTENSIONS:
        raise ValidationError(
            f'不支持的试卷文件类型: {ext}。允许的类型: {", ".join(ALLOWED_EXAM_PAPER_EXTENSIONS)}'
        )
    if file.size > MAX_EXAM_PAPER_SIZE:
        raise ValidationError(
            f'试卷文件过大（{file.size // 1024 // 1024}MB），最大允许 {MAX_EXAM_PAPER_SIZE // 1024 // 1024}MB'
        )


# ==================== 考试列表与详情 ====================

@method_decorator(login_required, name='dispatch')
class ExamListView(ListView):
    """考试列表"""
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 10

    def get_queryset(self):
        return Exam.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取当前用户各考试的最好成绩
        if self.request.user.is_authenticated:
            user = self.request.user
            exam_ids = [exam.pk for exam in context['exams']]
            attempts = ExamAttempt.objects.filter(
                exam_id__in=exam_ids,
                user=user,
                status__in=['completed', 'timeout'],
            )
            best_scores = {}
            for attempt in attempts:
                if attempt.exam_id not in best_scores or (attempt.score or 0) > best_scores[attempt.exam_id]:
                    best_scores[attempt.exam_id] = attempt.score
            context['best_scores'] = best_scores
        return context


@login_required
@user_passes_test(is_admin)
def exam_detail_view(request, pk):
    """考试详情（管理员）- 显示题目信息"""
    exam = get_object_or_404(Exam, pk=pk)
    questions = exam.questions.all()
    attempts = exam.attempts.select_related('user').all()[:20]

    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'questions': questions,
        'attempts': attempts,
    })


@login_required
@user_passes_test(is_admin)
def exam_create_view(request):
    """创建考试（管理员）"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        course_id = request.POST.get('course')
        duration = request.POST.get('duration', '60')
        total_score = request.POST.get('total_score', '100')
        pass_score = request.POST.get('pass_score', '60')
        is_published = request.POST.get('is_published') == 'on'
        exam_paper = request.FILES.get('exam_paper')

        # 安全验证：检查试卷文件类型和大小
        if exam_paper:
            try:
                validate_exam_paper(exam_paper)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'exams/exam_form.html', {
                    'courses': Course.objects.all(),
                })

        if not title:
            messages.error(request, '考试标题不能为空。')
            return render(request, 'exams/exam_form.html', {
                'courses': Course.objects.all(),
            })

        try:
            duration = int(duration)
            total_score = int(total_score)
            pass_score = int(pass_score)
        except (ValueError, TypeError):
            messages.error(request, '分数和时长必须为整数。')
            return render(request, 'exams/exam_form.html', {
                'courses': Course.objects.all(),
            })

        exam = Exam.objects.create(
            title=title,
            description=description,
            course_id=course_id if course_id else None,
            duration=duration,
            total_score=total_score,
            pass_score=pass_score,
            is_published=is_published,
            created_by=request.user,
            exam_paper=exam_paper,
        )
        messages.success(request, f'考试 "{exam.title}" 创建成功！')
        return redirect('exams:detail', pk=exam.pk)

    return render(request, 'exams/exam_form.html', {
        'courses': Course.objects.all(),
    })


# ==================== 参加考试（核心功能） ====================

@login_required
def take_exam_view(request, pk):
    """参加考试

    核心功能：
    - 开始考试时创建 ExamAttempt
    - 显示所有题目，支持单选/多选/判断/填空/简答
    - 提交时自动评分（单选/多选/判断/填空自动评分，简答需手动评分）
    - 考试超时自动提交
    - 提交前需电子签名确认
    """
    from apps.signatures.models import Signature

    exam = get_object_or_404(Exam, pk=pk, is_published=True)

    # 检查是否有正在进行的考试
    attempt = ExamAttempt.objects.filter(
        exam=exam, user=request.user, status='in_progress'
    ).first()

    if not attempt:
        # 检查重考权限
        if not exam.allow_retake:
            passed_attempt = ExamAttempt.objects.filter(
                exam=exam, user=request.user, is_passed=True
            ).exists()
            if passed_attempt:
                messages.error(request, '您已通过此考试，不允许重复考试。')
                return redirect('exams:detail', exam.pk)

        if exam.max_attempts > 0:
            attempt_count = ExamAttempt.objects.filter(
                exam=exam, user=request.user
            ).count()
            if attempt_count >= exam.max_attempts:
                messages.error(request, f'您已达到最大考试次数（{exam.max_attempts}次），无法再次考试。')
                return redirect('exams:detail', exam.pk)

        # 检查强制培训时限
        from apps.plans.models import TrainingPlan, MandatoryTrainee
        plans = TrainingPlan.objects.filter(exams=exam, is_mandatory=True)
        for plan in plans:
            if plan.is_expired:
                try:
                    trainee = MandatoryTrainee.objects.get(plan=plan, user=request.user)
                    if trainee.status != 'passed':
                        messages.error(request, '培训已逾期，请联系管理员。')
                        return redirect('exams:detail', exam.pk)
                except MandatoryTrainee.DoesNotExist:
                    # 用户不在该强制培训名单中，跳过
                    pass

        attempt = ExamAttempt.objects.create(
            exam=exam,
            user=request.user,
        )

    # 检查是否已超时
    if attempt.is_timed_out():
        _submit_exam(attempt, exam, {})
        messages.warning(request, '考试已超时，系统已自动提交。')
        return redirect('exams:result', pk=exam.pk)

    questions = exam.questions.all()

    # 处理签名后的返回（GET 中带 signature_id）
    signature_id = request.GET.get('signature_id')
    pending_signature = None
    if signature_id:
        try:
            sig = Signature.objects.get(
                id=signature_id,
                signed_by=request.user,
                signature_type='exam'
            )
            pending_signature = sig
        except Signature.DoesNotExist:
            messages.error(request, '签名无效或不存在，请重新签名。')

    if request.method == 'POST':
        signature_id_post = request.POST.get('signature_id') or request.GET.get('signature_id')

        # 收集所有答案
        answers_data = {}
        for question in questions:
            key = f'question_{question.id}'
            if question.question_type == 'multi_choice':
                selected = request.POST.getlist(key)
                answers_data[question.id] = ','.join(sorted(selected))
            else:
                answers_data[question.id] = request.POST.get(key, '')

        # 再次检查是否超时
        if attempt.is_timed_out():
            _submit_exam(attempt, exam, answers_data, signature_id=signature_id_post)
            messages.warning(request, '考试已超时，系统已自动提交。')
            return redirect('exams:result', pk=exam.pk)

        _submit_exam(attempt, exam, answers_data, signature_id=signature_id_post)

        # 更新强制培训状态
        from apps.plans.models import TrainingPlan, MandatoryTrainee
        plans = TrainingPlan.objects.filter(
            exams=attempt.exam,
            is_mandatory=True
        )
        for plan in plans:
            try:
                trainee = MandatoryTrainee.objects.get(plan=plan, user=request.user)
                trainee.update_status_after_exam(attempt.score or 0, attempt.is_passed or False)
                if attempt.is_passed:
                    messages.success(request, '恭喜！您已通过考试，强制培训任务已完成。')
                else:
                    if trainee.can_retake_exam():
                        messages.warning(request,
                            f'考试未通过（{attempt.score}分），您需要继续学习并重新考试。'
                            f'已考 {trainee.exam_attempts} 次，'
                            f'{"不限次数" if plan.max_attempts == 0 else f"最多可考 {plan.max_attempts} 次"}。')
                    else:
                        messages.error(request, '培训已逾期或已达到最大考试次数，请联系管理员。')
            except MandatoryTrainee.DoesNotExist:
                pass

        messages.success(request, f'考试已提交！您的得分：{attempt.score}/{exam.total_score}')
        return redirect('exams:result', pk=exam.pk)

    # 计算剩余时间
    remaining_seconds = attempt.get_remaining_time()
    remaining_minutes = remaining_seconds // 60
    remaining_secs = remaining_seconds % 60

    # 获取已有答案（用于恢复之前填写的答案）
    existing_answers = {
        ans.question_id: ans.user_answer
        for ans in attempt.answers.all()
    }

    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'attempt': attempt,
        'questions': questions,
        'remaining_minutes': remaining_minutes,
        'remaining_seconds': remaining_secs,
        'existing_answers': existing_answers,
        'pending_signature': pending_signature,
    })


def _submit_exam(attempt, exam, answers_data, signature_id=None):
    """提交考试并自动评分

    单选/多选/判断/填空自动评分，简答标记为待手动评分。
    支持关联电子签名。
    """
    from apps.signatures.models import Signature

    questions = exam.questions.all()
    total_score = 0
    has_essay = False

    for question in questions:
        user_answer = answers_data.get(question.id, '')
        is_correct, score = question.check_answer(user_answer)

        if question.question_type == 'essay':
            has_essay = True

        Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'user_answer': user_answer,
                'is_correct': is_correct,
                'score': score,
            }
        )
        total_score += score

    # 判断是否超时
    if attempt.is_timed_out():
        attempt.status = 'timeout'
    else:
        attempt.status = 'completed'

    attempt.score = total_score
    attempt.end_time = timezone.now()
    attempt.is_passed = total_score >= exam.pass_score
    attempt.save()

    # 关联电子签名
    if signature_id:
        try:
            sig = Signature.objects.get(id=signature_id, signed_by=attempt.user)
            sig.content_object = attempt
            sig.save()
        except Signature.DoesNotExist:
            pass


# ==================== 考试结果 ====================

@login_required
def exam_result_view(request, pk):
    """查看考试结果"""
    from apps.signatures.models import Signature
    exam = get_object_or_404(Exam, pk=pk)

    # 获取当前用户该考试的最新一次记录
    attempt = ExamAttempt.objects.filter(
        exam=exam, user=request.user,
        status__in=['completed', 'timeout'],
    ).order_by('-start_time').first()

    if not attempt:
        messages.info(request, '您尚未参加此考试。')
        return redirect('exams:take', pk=pk)

    answers = attempt.answers.select_related('question').all()

    # 获取关联的签名
    signature = None
    try:
        signature = Signature.objects.filter(
            content_type__model='examattempt',
            object_id=attempt.id,
            signature_type='exam'
        ).first()
    except Exception:
        pass

    return render(request, 'exams/result.html', {
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'signature': signature,
    })


@login_required
@user_passes_test(is_admin)
def exam_score_view(request, pk):
    """管理员查看所有考试结果（含签名信息）"""
    from apps.signatures.models import Signature
    exam = get_object_or_404(Exam, pk=pk)
    attempts = exam.attempts.select_related('user').all().order_by('-start_time')

    # 预加载所有签名，避免 N+1 查询
    attempt_ids = [a.id for a in attempts]
    signatures_map = {}
    if attempt_ids:
        from django.contrib.contenttypes.models import ContentType
        attempt_ct = ContentType.objects.get_for_model(ExamAttempt)
        sigs = Signature.objects.filter(
            content_type=attempt_ct,
            object_id__in=attempt_ids,
            signature_type='exam'
        ).select_related('signed_by')
        for sig in sigs:
            signatures_map[sig.object_id] = sig

    return render(request, 'exams/exam_scores.html', {
        'exam': exam,
        'attempts': attempts,
        'signatures_map': signatures_map,
    })


# ==================== 答题留痕 API ====================

@login_required
@require_POST
def answer_log_api(request, attempt_pk):
    """答题留痕 API - 记录每次答案变更"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, user=request.user)

    # 只允许进行中的考试记录答题轨迹
    if attempt.status != 'in_progress':
        return JsonResponse({'error': '考试已结束，无法记录'}, status=400)

    data = json.loads(request.body)
    question_id = data.get('question_id')
    new_answer = data.get('new_answer', '')
    elapsed_seconds = data.get('elapsed_seconds', 0)

    question = get_object_or_404(Question, pk=question_id, exam=attempt.exam)

    # 获取上一次记录的值
    last_log = AnswerLog.objects.filter(
        attempt=attempt, question=question
    ).order_by('-created_at').first()

    old_answer = last_log.new_answer if last_log else ''

    # 判断操作类型
    if not old_answer and new_answer:
        action_type = 'answer'
    elif old_answer and not new_answer:
        action_type = 'delete'
    else:
        action_type = 'change'

    # 创建留痕记录
    log = AnswerLog.objects.create(
        attempt=attempt,
        question=question,
        old_answer=old_answer,
        new_answer=new_answer,
        action_type=action_type,
        elapsed_seconds=elapsed_seconds,
        ip_address=_get_client_ip(request),
    )

    return JsonResponse({
        'ok': True,
        'log_id': log.id,
        'action_type': action_type,
    })


@login_required
@user_passes_test(is_admin)
def exam_attempt_log_view(request, pk):
    """管理员查看答题留痕详情"""
    attempt = get_object_or_404(ExamAttempt, pk=pk)
    logs = attempt.answer_logs.select_related('question').order_by('created_at')

    # 按题目分组
    question_logs = {}
    for log in logs:
        qid = log.question_id
        if qid not in question_logs:
            question_logs[qid] = {
                'question': log.question,
                'logs': [],
            }
        question_logs[qid]['logs'].append(log)

    return render(request, 'exams/attempt_logs.html', {
        'attempt': attempt,
        'question_logs': question_logs,
    })


# ==================== 辅助函数 ====================

def _get_client_ip(request):
    """获取客户端 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


# ==================== 自动出卷 ====================

@login_required
@user_passes_test(is_admin)
def paper_template_list_view(request):
    """出卷模板列表"""
    templates = PaperTemplate.objects.filter(created_by=request.user).prefetch_related('rules')
    return render(request, 'exams/paper_template_list.html', {
        'templates': templates,
    })


@login_required
@user_passes_test(is_admin)
def paper_template_create_view(request):
    """创建出卷模板"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        duration = int(request.POST.get('duration', 60))
        pass_score = int(request.POST.get('pass_score', 60))

        if not name:
            messages.error(request, '模板名称不能为空。')
            return render(request, 'exams/paper_template_form.html', {})

        template = PaperTemplate.objects.create(
            name=name,
            description=description,
            duration=duration,
            pass_score=pass_score,
            created_by=request.user,
        )

        # 添加规则
        rule_types = request.POST.getlist('rule_type[]')
        rule_counts = request.POST.getlist('rule_count[]')
        rule_scores = request.POST.getlist('rule_score[]')
        rule_difficulties = request.POST.getlist('rule_difficulty[]')
        rule_kp_ids = request.POST.getlist('rule_kp_ids[]')

        for i, rtype in enumerate(rule_types):
            count = int(rule_counts[i]) if i < len(rule_counts) else 10
            score = int(rule_scores[i]) if i < len(rule_scores) else 5
            diff = rule_difficulties[i] if i < len(rule_difficulties) else 'mixed'
            kp_ids = rule_kp_ids[i] if i < len(rule_kp_ids) else ''

            PaperRule.objects.create(
                template=template,
                question_type=rtype,
                count=count,
                score_per_question=score,
                difficulty=diff,
                knowledge_point_ids=kp_ids,
                order=i,
            )

        messages.success(request, f'出卷模板 "{name}" 创建成功！')
        return redirect('exams:paper_template_list')

    return render(request, 'exams/paper_template_form.html', {
        'type_choices': Question.QUESTION_TYPE_CHOICES,
        'difficulty_choices': PaperRule._meta.get_field('difficulty').choices,
    })


@login_required
@user_passes_test(is_admin)
def paper_template_edit_view(request, pk):
    """编辑出卷模板"""
    template = get_object_or_404(PaperTemplate, pk=pk)
    if request.method == 'POST':
        template.name = request.POST.get('name', '').strip()
        template.description = request.POST.get('description', '').strip()
        template.duration = int(request.POST.get('duration', 60))
        template.pass_score = int(request.POST.get('pass_score', 60))
        template.save()

        # 删除旧规则，重新创建
        template.rules.all().delete()

        rule_types = request.POST.getlist('rule_type[]')
        rule_counts = request.POST.getlist('rule_count[]')
        rule_scores = request.POST.getlist('rule_score[]')
        rule_difficulties = request.POST.getlist('rule_difficulty[]')
        rule_kp_ids = request.POST.getlist('rule_kp_ids[]')

        for i, rtype in enumerate(rule_types):
            count = int(rule_counts[i]) if i < len(rule_counts) else 10
            score = int(rule_scores[i]) if i < len(rule_scores) else 5
            diff = rule_difficulties[i] if i < len(rule_difficulties) else 'mixed'
            kp_ids = rule_kp_ids[i] if i < len(rule_kp_ids) else ''

            PaperRule.objects.create(
                template=template,
                question_type=rtype,
                count=count,
                score_per_question=score,
                difficulty=diff,
                knowledge_point_ids=kp_ids,
                order=i,
            )

        messages.success(request, f'出卷模板 "{template.name}" 已更新。')
        return redirect('exams:paper_template_list')

    return render(request, 'exams/paper_template_form.html', {
        'template': template,
        'type_choices': Question.QUESTION_TYPE_CHOICES,
        'difficulty_choices': PaperRule._meta.get_field('difficulty').choices,
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def paper_template_delete_view(request, pk):
    """删除出卷模板"""
    template = get_object_or_404(PaperTemplate, pk=pk)
    template.delete()
    messages.success(request, '出卷模板已删除。')
    return redirect('exams:paper_template_list')


@login_required
@user_passes_test(is_admin)
def paper_generate_view(request, pk):
    """使用模板自动生成考试"""
    template = get_object_or_404(PaperTemplate, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        course_id = request.POST.get('course')
        is_published = request.POST.get('is_published') == 'on'

        if not title:
            messages.error(request, '考试标题不能为空。')
            return render(request, 'exams/paper_generate.html', {
                'template': template,
                'courses': Course.objects.all(),
            })

        try:
            exam = template.generate_exam(
                title=title,
                created_by=request.user,
                course=Course.objects.get(pk=course_id) if course_id else None,
            )
            if is_published:
                exam.is_published = True
                exam.save()
            messages.success(
                request,
                f'考试 "{exam.title}" 已自动生成！'
                f'共 {exam.questions.count()} 题，总分 {exam.total_score} 分。'
            )
            return redirect('exams:detail', pk=exam.pk)
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'exams/paper_generate.html', {
                'template': template,
                'courses': Course.objects.all(),
            })

    return render(request, 'exams/paper_generate.html', {
        'template': template,
        'courses': Course.objects.all(),
    })
