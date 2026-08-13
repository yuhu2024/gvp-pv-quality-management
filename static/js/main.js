/**
 * 君合盟药物警戒培训管理系统 - 全局JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

    // =============================================
    // 1. 消息自动关闭（5秒后）
    // =============================================
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // =============================================
    // 2. 文件上传大小检查（100MB限制）
    // =============================================
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            var maxSize = 100 * 1024 * 1024; // 100MB
            if (this.files && this.files[0]) {
                var file = this.files[0];
                if (file.size > maxSize) {
                    alert('文件 "' + file.name + '" 大小为 ' + formatFileSize(file.size) +
                        '，超过100MB限制，请选择更小的文件。');
                    this.value = '';
                }
            }
        });
    });

    // =============================================
    // 3. 表单提交确认对话框
    // =============================================
    // data-confirm 属性的表单
    var confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            var message = form.getAttribute('data-confirm') || '确定要执行此操作吗？';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // data-confirm 属性的链接/按钮
    var confirmElements = document.querySelectorAll('a[data-confirm], button[data-confirm]');
    confirmElements.forEach(function (el) {
        el.addEventListener('click', function (e) {
            var message = this.getAttribute('data-confirm') || '确定要执行此操作吗？';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopImmediatePropagation();
                return false;
            }
        });
    });

    // =============================================
    // 4. 搜索输入防抖
    // =============================================
    var searchInputs = document.querySelectorAll('[data-debounce]');
    searchInputs.forEach(function (input) {
        var timer = null;
        var delay = parseInt(input.getAttribute('data-debounce')) || 500;
        input.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(function () {
                input.form.submit();
            }, delay);
        });
    });

    // =============================================
    // 5. 回到顶部按钮
    // =============================================
    var scrollTopBtn = document.querySelector('.scroll-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                scrollTopBtn.style.display = 'flex';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });
        scrollTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // =============================================
    // 6. 全选/取消全选功能（用于批量分配任务等）
    // =============================================
    var selectAllCheckbox = document.querySelector('[data-select-all]');
    if (selectAllCheckbox) {
        var targetName = selectAllCheckbox.getAttribute('data-select-all');
        var checkboxes = document.querySelectorAll('input[name="' + targetName + '"]');

        selectAllCheckbox.addEventListener('change', function () {
            var isChecked = this.checked;
            checkboxes.forEach(function (cb) {
                cb.checked = isChecked;
                // 触发 change 事件以便其他逻辑可以响应
                cb.dispatchEvent(new Event('change'));
            });
            updateSelectAllState(selectAllCheckbox, targetName);
        });

        // 监听单个复选框的变化，更新全选状态
        checkboxes.forEach(function (cb) {
            cb.addEventListener('change', function () {
                updateSelectAllState(selectAllCheckbox, targetName);
            });
        });
    }

    // =============================================
    // 7. 拖拽上传区域
    // =============================================
    var uploadAreas = document.querySelectorAll('.upload-area');
    uploadAreas.forEach(function (area) {
        var fileInput = area.querySelector('input[type="file"]');

        ['dragenter', 'dragover'].forEach(function (eventName) {
            area.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                area.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            area.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                area.classList.remove('dragover');
            });
        });

        area.addEventListener('drop', function (e) {
            var files = e.dataTransfer.files;
            if (fileInput && files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });

        // 点击上传区域触发文件选择
        if (fileInput) {
            area.addEventListener('click', function (e) {
                if (e.target !== fileInput) {
                    fileInput.click();
                }
            });
        }
    });

    // =============================================
    // 8. 工具提示（Tooltip）初始化
    // =============================================
    var tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // =============================================
    // 9. 自动保存提示（离开页面时）
    // =============================================
    var autoSaveForms = document.querySelectorAll('form[data-auto-save-warning]');
    autoSaveForms.forEach(function (form) {
        var hasChanges = false;
        var inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function (input) {
            input.addEventListener('input', function () {
                hasChanges = true;
            });
        });

        window.addEventListener('beforeunload', function (e) {
            if (hasChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        form.addEventListener('submit', function () {
            hasChanges = false;
        });
    });
});

// =============================================
// 辅助函数
// =============================================

/**
 * 更新全选复选框的状态
 * @param {HTMLElement} selectAll - 全选复选框元素
 * @param {string} targetName - 目标复选框的name属性
 */
function updateSelectAllState(selectAll, targetName) {
    var checkboxes = document.querySelectorAll('input[name="' + targetName + '"]');
    var total = checkboxes.length;
    var checked = document.querySelectorAll('input[name="' + targetName + '"]:checked').length;

    if (total === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checked === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checked === total) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }

    // 更新选中计数显示
    var countDisplay = document.querySelector('[data-select-count="' + targetName + '"]');
    if (countDisplay) {
        countDisplay.textContent = '已选择 ' + checked + ' 项';
        countDisplay.style.display = checked > 0 ? 'inline' : 'none';
    }
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小字符串
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    var k = 1024;
    var sizes = ['B', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 获取选中的复选框值
 * @param {string} name - 复选框的name属性
 * @returns {Array} 选中的值数组
 */
function getSelectedValues(name) {
    var values = [];
    var checkboxes = document.querySelectorAll('input[name="' + name + '"]:checked');
    checkboxes.forEach(function (cb) {
        values.push(cb.value);
    });
    return values;
}

/**
 * 确认删除对话框（使用自定义模态框替代原生confirm）
 * @param {string} message - 确认消息
 * @param {Function} onConfirm - 确认后的回调函数
 */
function confirmDelete(message, onConfirm) {
    // 尝试使用Bootstrap模态框
    var modalEl = document.getElementById('confirmModal');
    if (modalEl) {
        var modalBody = modalEl.querySelector('.modal-body');
        var confirmBtn = modalEl.querySelector('[data-confirm-action]');
        if (modalBody) {
            modalBody.textContent = message;
        }
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        if (confirmBtn) {
            // 移除旧的事件监听器
            var newBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
            newBtn.addEventListener('click', function () {
                modal.hide();
                if (typeof onConfirm === 'function') {
                    onConfirm();
                }
            });
        }
        modal.show();
    } else {
        // 回退到原生confirm
        if (confirm(message || '确定要删除吗？此操作不可恢复。')) {
            if (typeof onConfirm === 'function') {
                onConfirm();
            }
        }
    }
}

// =============================================
// 考试倒计时功能
// =============================================

/**
 * 考试倒计时器
 * @param {string} timerElementId - 计时器显示元素的ID
 * @param {number} totalSeconds - 总秒数
 * @param {Function} onTimeUp - 时间到时的回调函数
 * @returns {Object} 计时器控制对象
 */
function ExamTimer(timerElementId, totalSeconds, onTimeUp) {
    this.timerElement = document.getElementById(timerElementId);
    this.totalSeconds = totalSeconds;
    this.remainingSeconds = totalSeconds;
    this.onTimeUp = onTimeUp;
    this.intervalId = null;
    this.isRunning = false;

    if (!this.timerElement) {
        console.error('计时器元素不存在: ' + timerElementId);
        return;
    }

    this.updateDisplay();
}

/**
 * 启动计时器
 */
ExamTimer.prototype.start = function () {
    if (this.isRunning) return;
    this.isRunning = true;

    var self = this;
    this.intervalId = setInterval(function () {
        self.remainingSeconds--;

        if (self.remainingSeconds <= 0) {
            self.remainingSeconds = 0;
            self.stop();
            self.updateDisplay();
            if (typeof self.onTimeUp === 'function') {
                self.onTimeUp();
            }
            return;
        }

        self.updateDisplay();
    }, 1000);
};

/**
 * 停止计时器
 */
ExamTimer.prototype.stop = function () {
    if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
    }
    this.isRunning = false;
};

/**
 * 更新计时器显示
 */
ExamTimer.prototype.updateDisplay = function () {
    if (!this.timerElement) return;

    var hours = Math.floor(this.remainingSeconds / 3600);
    var minutes = Math.floor((this.remainingSeconds % 3600) / 60);
    var seconds = this.remainingSeconds % 60;

    var timeStr = '';
    if (hours > 0) {
        timeStr = padZero(hours) + ':' + padZero(minutes) + ':' + padZero(seconds);
    } else {
        timeStr = padZero(minutes) + ':' + padZero(seconds);
    }

    // 更新显示值
    var valueEl = this.timerElement.querySelector('.timer-value');
    if (valueEl) {
        valueEl.textContent = timeStr;
    } else {
        this.timerElement.textContent = timeStr;
    }

    // 更新样式状态
    this.timerElement.classList.remove('warning', 'danger');
    if (this.remainingSeconds <= 60) {
        this.timerElement.classList.add('danger');
    } else if (this.remainingSeconds <= 300) {
        this.timerElement.classList.add('warning');
    }

    // 更新页面标题
    if (this.remainingSeconds <= 300) {
        document.title = '[' + timeStr + '] 考试中';
    }
};

/**
 * 获取剩余时间（秒）
 * @returns {number}
 */
ExamTimer.prototype.getRemaining = function () {
    return this.remainingSeconds;
};

/**
 * 补零
 * @param {number} num
 * @returns {string}
 */
function padZero(num) {
    return num < 10 ? '0' + num : '' + num;
}

// =============================================
// 表单验证辅助函数
// =============================================

/**
 * 验证必填字段
 * @param {HTMLFormElement} form - 表单元素
 * @returns {boolean} 是否通过验证
 */
function validateRequiredFields(form) {
    var isValid = true;
    var requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(function (field) {
        // 清除旧的验证状态
        field.classList.remove('is-invalid');
        var feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) feedback.remove();

        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');

            var feedbackEl = document.createElement('div');
            feedbackEl.className = 'invalid-feedback';
            feedbackEl.textContent = '此字段为必填项';
            field.parentNode.appendChild(feedbackEl);
        }
    });

    return isValid;
}

/**
 * 验证表单并阻止无效提交
 * @param {string} formId - 表单ID
 * @param {Function} onSubmit - 验证通过后的回调
 */
function validateAndSubmit(formId, onSubmit) {
    var form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        if (validateRequiredFields(form)) {
            if (typeof onSubmit === 'function') {
                onSubmit(form);
            } else {
                form.submit();
            }
        } else {
            // 滚动到第一个无效字段
            var firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
        }
    });
}

/**
 * 实时验证单个字段
 * @param {HTMLElement} field - 输入字段
 * @param {Function} validator - 验证函数，返回错误消息或null
 */
function validateField(field, validator) {
    field.addEventListener('input', function () {
        var errorMsg = validator(field.value);
        field.classList.remove('is-invalid', 'is-valid');

        var feedback = field.parentNode.querySelector('.invalid-feedback');
        if (feedback) feedback.remove();

        if (errorMsg) {
            field.classList.add('is-invalid');
            var feedbackEl = document.createElement('div');
            feedbackEl.className = 'invalid-feedback';
            feedbackEl.textContent = errorMsg;
            field.parentNode.appendChild(feedbackEl);
        } else if (field.value.trim()) {
            field.classList.add('is-valid');
        }
    });
}

/**
 * 验证最小/最大长度
 * @param {HTMLElement} field - 输入字段
 * @param {number} min - 最小长度
 * @param {number} max - 最大长度
 * @returns {string|null} 错误消息或null
 */
function validateLength(field, min, max) {
    var val = field.value.trim();
    if (val.length === 0) return null;
    if (min && val.length < min) {
        return '最少需要输入 ' + min + ' 个字符';
    }
    if (max && val.length > max) {
        return '最多只能输入 ' + max + ' 个字符';
    }
    return null;
}

// =============================================
// 答题卡交互
// =============================================

/**
 * 更新答题卡状态
 * @param {number} questionIndex - 题目索引（从0开始）
 * @param {string} state - 状态: 'answered', 'current', 'flagged', ''
 */
function updateAnswerSheetItem(questionIndex, state) {
    var item = document.querySelector('.answer-sheet-item[data-question="' + questionIndex + '"]');
    if (item) {
        item.classList.remove('answered', 'current', 'flagged');
        if (state) {
            item.classList.add(state);
        }
    }
}

/**
 * 滚动到指定题目
 * @param {number} questionIndex - 题目索引
 */
function scrollToQuestion(questionIndex) {
    var questionEl = document.querySelector('.question-card[data-question="' + questionIndex + '"]');
    if (questionEl) {
        questionEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// =============================================
// 进度条动画
// =============================================

/**
 * 动画更新进度条
 * @param {string} elementId - 进度条元素ID
 * @param {number} percentage - 百分比 (0-100)
 * @param {string} label - 可选的标签文本
 */
function animateProgress(elementId, percentage, label) {
    var progressBar = document.getElementById(elementId);
    if (!progressBar) return;

    var bar = progressBar.querySelector('.progress-bar');
    if (bar) {
        // 使用 requestAnimationFrame 实现平滑动画
        var currentWidth = parseFloat(bar.style.width) || 0;
        var targetWidth = Math.min(100, Math.max(0, percentage));
        var step = (targetWidth - currentWidth) / 20;

        function animate() {
            currentWidth += step;
            if ((step > 0 && currentWidth >= targetWidth) ||
                (step < 0 && currentWidth <= targetWidth)) {
                bar.style.width = targetWidth + '%';
                if (label) {
                    bar.textContent = label || targetWidth + '%';
                }
                return;
            }
            bar.style.width = currentWidth + '%';
            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    }
}
